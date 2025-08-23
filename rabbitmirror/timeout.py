#!/usr/bin/env python3
"""
Hybrid, thread-safe timeout utilities supporting signal, thread, and process modes.

This module provides:
- TimeoutToken: a cooperative cancellation token for thread-based timeouts.
- run_with_timeout: a function to execute a callable with a timeout in either
  signal (main-thread only), thread (cooperative), process (hard) mode, or
  automatically choose between signal/thread via "auto" mode.
- timeout decorator: a decorator facade over run_with_timeout.

Design notes (macOS/arm64 friendly):
- Signal mode (SIGALRM) only works in the main thread and on POSIX systems.
  It provides strong, low-overhead timeouts for backward compatibility.
- Thread mode cannot forcibly kill a running thread. It signals via TimeoutToken
  and raises CustomTimeoutError to the caller. The worker must periodically
  check the token to stop early.
- Process mode uses multiprocessing (spawn start method on macOS). It can
  terminate the worker on timeout, providing stronger guarantees for CPU-bound
  or non-cooperative code. Target function and arguments must be pickleable.

This file avoids starting processes at import time; all process usage happens
inside functions to remain spawn-safe under pytest on macOS.
"""
from __future__ import annotations

import inspect
import multiprocessing as mp
import queue
import threading
import time
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

try:
    import signal
except Exception:  # pragma: no cover - signal not present on some platforms
    signal = None  # type: ignore[assignment]

from .exceptions import CustomTimeoutError


@dataclass
class TimeoutResult:
    ok: bool
    value: Any = None
    error: Optional[BaseException] = None
    tb: Optional[str] = None


class TimeoutToken:
    """Cooperative cancellation token for thread-based tasks.

    Workers can receive this token (via a "timeout_token" kwarg if present in the
    function signature) and periodically call token.raise_if_cancelled() or
    token.cancelled() to honor cancellation.
    """

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def cancelled(self) -> bool:
        return self._event.is_set()

    def raise_if_cancelled(self) -> None:
        if self.cancelled():
            raise CustomTimeoutError(
                "Operation cancelled by timeout",
                error_code="THREAD_TIMEOUT_CANCELLED",
            )


def _thread_worker(
    func: Callable[..., Any],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    out: queue.Queue,
    token: TimeoutToken,
) -> None:
    try:
        # Inject token if the function accepts it
        sig = inspect.signature(func)
        if "timeout_token" in sig.parameters and "timeout_token" not in kwargs:
            kwargs = {**kwargs, "timeout_token": token}
        result = func(*args, **kwargs)
        out.put(TimeoutResult(ok=True, value=result))
    except BaseException as e:  # capture any exception, including KeyboardInterrupt
        out.put(TimeoutResult(ok=False, error=e, tb=traceback.format_exc()))


def _process_worker(
    func: Callable[..., Any], args: Tuple[Any, ...], kwargs: Dict[str, Any], q: mp.Queue
) -> None:
    try:
        result = func(*args, **kwargs)
        q.put((True, result, None))
    except BaseException as e:
        q.put((False, e, traceback.format_exc()))


def _can_use_signal_mode() -> bool:
    if signal is None:
        return False
    # SIGALRM is not available on some platforms (e.g., Windows)
    if not hasattr(signal, "SIGALRM"):
        return False
    # Only main thread may set signal handlers
    return threading.current_thread() is threading.main_thread()


def _run_with_signal_timeout(
    func: Callable[..., Any],
    timeout_seconds: float,
    *args: Any,
    **kwargs: Any,
) -> Any:
    if timeout_seconds == 0:
        # Zero means no timeout; execute directly for consistency with other modes
        return func(*args, **kwargs)

    if signal is None or not hasattr(signal, "SIGALRM"):
        raise RuntimeError("Signal-based timeout is not supported on this platform")

    # Define handler that raises our CustomTimeoutError
    def _alarm_handler(signum, frame):  # type: ignore[no-untyped-def]
        raise CustomTimeoutError(
            f"Operation timed out after {timeout_seconds} seconds (signal mode)",
            timeout_duration=timeout_seconds,
            error_code="SIGNAL_TIMEOUT",
        )

    old_handler = signal.getsignal(signal.SIGALRM)
    try:
        signal.signal(signal.SIGALRM, _alarm_handler)
        # Use setitimer for sub-second precision if available, else alarm()
        if hasattr(signal, "setitimer"):
            signal.setitimer(signal.ITIMER_REAL, timeout_seconds)
        else:
            # alarm() takes integer seconds; ceiling for safety
            alarm_secs = (
                int(timeout_seconds)
                if timeout_seconds.is_integer()
                else int(timeout_seconds) + 1
            )
            signal.alarm(alarm_secs)
        return func(*args, **kwargs)
    finally:
        # Always cancel alarm and restore handler to avoid leaking state
        try:
            if hasattr(signal, "setitimer"):
                signal.setitimer(signal.ITIMER_REAL, 0)
            else:
                signal.alarm(0)
        finally:
            signal.signal(signal.SIGALRM, old_handler)


def run_with_timeout(
    func: Callable[..., Any],
    timeout_seconds: float,
    *args: Any,
    mode: str = "thread",  # "auto", "signal", "thread", or "process"
    grace_period: float = 0.1,
    **kwargs: Any,
) -> Any:
    """Run a function with a timeout in signal, thread, process, or auto mode.

    Parameters:
    - func: Callable to execute. In thread mode, if it accepts a "timeout_token"
      kwarg, a cooperative TimeoutToken will be passed.
    - timeout_seconds: Maximum time to wait for completion.
    - mode: One of "auto" (signal in main thread, else thread), "signal"
      (main-thread SIGALRM), "thread" (cooperative), or "process" (hard timeout).
    - grace_period: Additional best-effort wait after signalling timeout (thread mode)
      or after terminate() (process mode) to let resources settle.
    - *args, **kwargs: Passed to func.

    Returns: func's return value on success.
    Raises: CustomTimeoutError on timeout, or re-raises func's exception.
    """
    if timeout_seconds < 0:
        raise ValueError("timeout_seconds must be non-negative")

    # Backward compatibility: zero means no timeout; execute directly in any mode
    if timeout_seconds == 0:
        # If the target cooperatively accepts a timeout_token, inject one for compatibility
        try:
            sig = inspect.signature(func)
            if "timeout_token" in sig.parameters and "timeout_token" not in kwargs:
                kwargs = {**kwargs, "timeout_token": TimeoutToken()}
        except Exception:
            # Fallback: if signature inspection fails, proceed without injecting a token.
            # nosec B110 - intentional empty except to preserve behavior across runtimes
            pass
        return func(*args, **kwargs)

    if mode not in ("auto", "signal", "thread", "process"):
        raise ValueError("mode must be 'auto', 'signal', 'thread', or 'process'")

    # Auto-select between signal and thread for thread-safety and backward compat
    if mode == "auto":
        if _can_use_signal_mode():
            mode = "signal"
        else:
            mode = "thread"

    if mode == "signal":
        if not _can_use_signal_mode():
            # Fallback gracefully to thread mode when not in main thread or unsupported
            mode = "thread"
        else:
            return _run_with_signal_timeout(func, timeout_seconds, *args, **kwargs)

    if mode == "thread":
        q: queue.Queue = queue.Queue(maxsize=1)
        token = TimeoutToken()
        t = threading.Thread(
            target=_thread_worker, args=(func, args, kwargs, q, token), daemon=True
        )
        t.start()
        t.join(timeout_seconds)
        if t.is_alive():
            # Signal cooperative cancellation and raise to caller
            token.cancel()
            # Give the worker a brief moment to observe cancellation
            t.join(grace_period)
            raise CustomTimeoutError(
                f"Operation timed out after {timeout_seconds} seconds (thread mode)",
                timeout_duration=timeout_seconds,
                error_code="THREAD_TIMEOUT",
            )
        # Collect result
        try:
            res: TimeoutResult = q.get_nowait()
        except queue.Empty:
            # Should not happen, but handle defensively
            raise RuntimeError("No result from thread worker")
        if res.ok:
            return res.value
        if res.error is None:
            raise RuntimeError("Thread worker failed without an error object")
        raise res.error

    # process mode
    # Prefer 'fork' on POSIX if available for better pickling compatibility (e.g., local functions)
    # Fallback to 'spawn' (default on macOS) when 'fork' is unavailable.
    start_method = "spawn"
    try:
        available = mp.get_all_start_methods()
        if "fork" in available:
            start_method = "fork"
    except Exception:
        # If querying start methods fails, default to spawn which is safe on macOS
        # nosec B110 - benign fallback
        pass
    ctx = mp.get_context(start_method)
    q: mp.Queue = ctx.Queue(maxsize=1)
    p = ctx.Process(target=_process_worker, args=(func, args, kwargs, q))
    p.daemon = False  # ensure proper cleanup semantics
    p.start()
    p.join(timeout_seconds)
    if p.is_alive():
        # Hard timeout: terminate the process
        p.terminate()
        p.join(grace_period)
        # Ensure process is gone
        if p.is_alive():
            # As a last resort, try kill() if available (Python 3.7+)
            try:
                p.kill()  # type: ignore[attr-defined]
                p.join(grace_period)
            except Exception:
                # If kill() is unavailable or fails, proceed to raise the timeout
                # nosec B110 - best-effort cleanup
                pass
        raise CustomTimeoutError(
            f"Operation timed out after {timeout_seconds} seconds (process mode)",
            timeout_duration=timeout_seconds,
            error_code="PROCESS_TIMEOUT",
        )

    # Retrieve result from queue
    if q.empty():
        # Worker exited without placing a result; treat as error
        raise RuntimeError("Worker process exited without returning a result")
    ok, value, tb = q.get()
    if ok:
        return value
    # Re-raise error preserving basic info; original traceback is in tb
    if isinstance(value, BaseException):
        raise value
    raise RuntimeError(f"Worker raised non-exception: {value}\n{tb}")


def timeout(
    timeout_seconds: float,
    mode: str = "auto",
    grace_period: float = 0.1,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to run a function with a timeout using the selected mode.

    Modes:
      - auto: use SIGALRM in main thread when available, otherwise thread mode
      - signal: enforce SIGALRM (falls back to thread mode if unavailable)
      - thread: cooperative thread-based timeout with TimeoutToken
      - process: hard timeout using a separate process

    Example:
        @timeout(2.0, mode="process")
        def compute(x):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return run_with_timeout(
                func,
                timeout_seconds,
                *args,
                mode=mode,
                grace_period=grace_period,
                **kwargs,
            )

        # Preserve metadata
        wrapped.__name__ = getattr(func, "__name__", "wrapped")
        wrapped.__doc__ = func.__doc__
        wrapped.__qualname__ = getattr(func, "__qualname__", wrapped.__name__)
        return wrapped

    return decorator


__all__ = [
    "TimeoutToken",
    "run_with_timeout",
    "timeout",
]
