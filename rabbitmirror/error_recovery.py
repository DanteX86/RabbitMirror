#!/usr/bin/env python3

"""
Advanced error handling with retry mechanisms and recovery strategies.

This module provides sophisticated error recovery capabilities including:
- Automatic retry mechanisms with exponential backoff
- Fallback strategies for common failures
- Error context preservation through retries
- Configurable recovery policies
"""

import asyncio
import functools
import logging
import secrets
import signal
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type

from .exceptions import (
    CustomTimeoutError,
    FileOperationError,
    NetworkError,
    ResourceError,
    create_error_context,
)


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
    ):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if base_delay < 0:
            raise ValueError("base_delay must be non-negative")
        if max_delay < base_delay:
            raise ValueError("max_delay must be greater than or equal to base_delay")
        if exponential_base < 1:
            raise ValueError("exponential_base must be at least 1")

        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [
            NetworkError,
            FileOperationError,
            CustomTimeoutError,
            ResourceError,
        ]


class CircuitBreaker:
    """Circuit breaker pattern implementation for error handling."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception,
    ):
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout must be non-negative")
        if not issubclass(expected_exception, Exception):
            raise ValueError("expected_exception must be an Exception subclass")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise ResourceError(
                    "Circuit breaker is OPEN. Service unavailable.",
                    error_code="CIRCUIT_BREAKER_OPEN",
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if self.last_failure_time is None:
            return True
        return (
            datetime.now() - self.last_failure_time
        ).total_seconds() > self.recovery_timeout

    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ErrorRecoveryManager:
    """Manages error recovery strategies and policies."""

    def __init__(self):
        self.recovery_strategies = {}
        self.circuit_breakers = {}
        self.logger = logging.getLogger(__name__)

    def register_recovery_strategy(
        self,
        error_type: Type[Exception],
        strategy: Callable[[Exception], Any],
    ):
        """Register a recovery strategy for a specific error type."""
        self.recovery_strategies[error_type] = strategy

    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]

    def attempt_recovery(self, error: Exception, context: Dict[str, Any]) -> Any:
        """Attempt to recover from an error using registered strategies."""
        for error_type, strategy in self.recovery_strategies.items():
            if isinstance(error, error_type):
                try:
                    return strategy(error)
                except (ValueError, TypeError, AttributeError) as recovery_error:
                    self.logger.warning(
                        "Recovery strategy failed for %s: %s",
                        error_type.__name__,
                        recovery_error,
                    )
                except Exception as recovery_error:
                    self.logger.error(
                        "Unexpected error in recovery strategy for %s: %s",
                        error_type.__name__,
                        recovery_error,
                    )

        # No recovery strategy found
        raise error


# Global error recovery manager
error_recovery_manager = ErrorRecoveryManager()


def with_retry(
    config: Optional[RetryConfig] = None,
    recovery_manager: Optional[ErrorRecoveryManager] = None,
) -> Callable:
    """Decorator to add retry functionality to functions."""
    if config is None:
        config = RetryConfig()

    if recovery_manager is None:
        recovery_manager = error_recovery_manager

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this exception is retryable
                    if not any(
                        isinstance(e, exc_type)
                        for exc_type in config.retryable_exceptions
                    ):
                        # Try recovery before giving up
                        context = create_error_context(
                            f"{func.__name__}_retry",
                            attempt=attempt + 1,
                            max_attempts=config.max_attempts,
                        )

                        try:
                            return recovery_manager.attempt_recovery(e, context)
                        except (ValueError, TypeError, AttributeError):
                            raise e from None
                        except Exception as recovery_error:
                            logging.error(
                                "Recovery failed for %s: %s",
                                func.__name__,
                                recovery_error,
                            )
                            raise e from None

                    # Calculate delay for next attempt
                    if attempt < config.max_attempts - 1:
                        delay = min(
                            config.base_delay * (config.exponential_base**attempt),
                            config.max_delay,
                        )

                        if config.jitter:
                            delay *= 0.5 + secrets.SystemRandom().random() * 0.5

                        time.sleep(delay)

            # All attempts failed
            raise last_exception

        return wrapper

    return decorator


def with_circuit_breaker(
    service_name: str,
    circuit_breaker_config: Optional[Dict[str, Any]] = None,
) -> Callable:
    """Decorator to add circuit breaker protection to functions."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            circuit_breaker = error_recovery_manager.get_circuit_breaker(service_name)

            if circuit_breaker_config:
                # Update circuit breaker configuration
                for key, value in circuit_breaker_config.items():
                    setattr(circuit_breaker, key, value)

            return circuit_breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator


def with_timeout(timeout_seconds: float) -> Callable:
    """Decorator to add timeout protection to functions in a thread-safe way.

    Strategy selection (auto):
    - If running in the main process and the target function appears picklable,
      execute it in a separate process so it can be forcefully terminated on timeout.
    - Otherwise, fall back to a thread-based execution that raises a timeout if the
      thread doesn't finish in time. Note: Python cannot safely kill threads; in
      this case, the worker thread is marked as daemon and will be cleaned up when
      the process exits.

    Edge cases handled:
    - Nested timeouts and recursive calls: a context variable tracks nesting depth.
      For nested timeouts or when already in a child process, the decorator uses
      the thread-based strategy to avoid spawning multiple processes.

    Function metadata is preserved via functools.wraps.
    """

    import contextvars
    import multiprocessing as mp
    import pickle
    import threading

    # Track nested timeouts to avoid spawning nested workers
    _timeout_depth: contextvars.ContextVar[int] = contextvars.ContextVar(
        "_timeout_depth", default=0
    )

    def _is_picklable(obj: Any) -> bool:
        try:
            pickle.dumps(obj)
            return True
        except Exception:
            return False

    def _run_in_process(func: Callable, args, kwargs, timeout: float):
        # Use a Queue to transfer result/exception
        q: mp.Queue = mp.Queue()

        def _target(q_: mp.Queue, f: Callable, a, kw):
            try:
                res = f(*a, **kw)
                q_.put(("result", res))
            except Exception as e:  # Must be pickleable
                try:
                    q_.put(("error", (e.__class__, str(e))))
                except Exception:
                    # Fallback when exception isn't pickleable
                    q_.put(("error", (Exception, "Unpickleable exception in worker")))

        proc = mp.Process(target=_target, args=(q, func, args, kwargs), daemon=True)
        proc.start()
        proc.join(timeout)

        if proc.is_alive():
            # Timeout: terminate process and clean up
            proc.terminate()
            proc.join(1.0)
            try:
                q.close()
            except Exception:
                pass
            raise CustomTimeoutError(
                f"Operation timed out after {timeout} seconds",
                timeout_duration=timeout,
                error_code="OPERATION_TIMEOUT",
            )

        # Process finished; fetch result
        try:
            kind, payload = q.get_nowait()
        except Exception:
            # Nothing in queue -> abnormal termination
            raise RuntimeError("Worker process exited without returning a result")
        finally:
            try:
                q.close()
            except Exception:
                pass

        if kind == "result":
            return payload
        else:
            exc_type, msg = payload
            raise exc_type(msg)

    def _run_in_thread(func: Callable, args, kwargs, timeout: float):
        # Soft timeout: cannot kill threads; we raise timeout if still running
        result_holder = {"result": None, "error": None}
        done = threading.Event()

        def _target():
            try:
                result_holder["result"] = func(*args, **kwargs)
            except Exception as e:
                result_holder["error"] = e
            finally:
                done.set()

        t = threading.Thread(target=_target, daemon=True)
        t.start()
        finished = done.wait(timeout)
        if not finished:
            # No safe way to kill a thread; leave daemon thread running
            raise CustomTimeoutError(
                f"Operation timed out after {timeout} seconds",
                timeout_duration=timeout,
                error_code="OPERATION_TIMEOUT",
            )
        if result_holder["error"] is not None:
            raise result_holder["error"]
        return result_holder["result"]

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Non-positive timeout means no timeout enforcement
            if not timeout_seconds or timeout_seconds <= 0:
                return func(*args, **kwargs)

            # Detect nesting and process context
            depth = _timeout_depth.get()
            in_main_process = mp.current_process().name == "MainProcess"

            token = _timeout_depth.set(depth + 1)
            try:
                # Avoid spawning processes in nested contexts or non-main processes
                use_process = (
                    depth == 0
                    and in_main_process
                    and _is_picklable(func)
                    and _is_picklable((args, kwargs))
                )

                if use_process:
                    return _run_in_process(func, args, kwargs, float(timeout_seconds))
                else:
                    return _run_in_thread(func, args, kwargs, float(timeout_seconds))
            finally:
                _timeout_depth.reset(token)

        return wrapper

    return decorator


def with_fallback(fallback_func: Callable) -> Callable:
    """Decorator to provide fallback functionality on error."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the original error
                logging.warning(
                    "Function %s failed: %s, using fallback", func.__name__, e
                )

                # Try fallback
                try:
                    return fallback_func(*args, **kwargs)
                except (ValueError, TypeError, AttributeError) as fallback_error:
                    # If fallback fails with common errors, raise the original error
                    raise e from fallback_error
                except Exception as fallback_error:
                    # For unexpected fallback errors, log and raise original
                    logging.error(
                        "Fallback for %s also failed: %s", func.__name__, fallback_error
                    )
                    raise e from fallback_error

        return wrapper

    return decorator


def robust_operation(
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker_service: Optional[str] = None,
    timeout_seconds: Optional[float] = None,
    fallback_func: Optional[Callable] = None,
) -> Callable:
    """Decorator that combines multiple error handling strategies."""

    def decorator(func: Callable) -> Callable:
        # Apply decorators in order
        wrapped_func = func

        # Apply fallback first (innermost)
        if fallback_func:
            wrapped_func = with_fallback(fallback_func)(wrapped_func)

        # Apply timeout
        if timeout_seconds:
            wrapped_func = with_timeout(timeout_seconds)(wrapped_func)

        # Apply circuit breaker
        if circuit_breaker_service:
            wrapped_func = with_circuit_breaker(circuit_breaker_service)(wrapped_func)

        # Apply retry (outermost)
        if retry_config:
            wrapped_func = with_retry(retry_config)(wrapped_func)

        return wrapped_func

    return decorator


# Pre-configured recovery strategies
def file_operation_recovery(error: FileOperationError) -> Any:
    """Recovery strategy for file operations."""
    if "Permission denied" in str(error):
        raise ResourceError(
            "Insufficient permissions for file operation. "
            "Please check file permissions and try again.",
            error_code="PERMISSION_DENIED_RECOVERY",
        )
    if "No space left on device" in str(error):
        raise ResourceError(
            "Disk space full. Please free up space and try again.",
            error_code="DISK_FULL_RECOVERY",
        )
    # Re-raise if no specific recovery available
    raise error


def network_operation_recovery(error: NetworkError) -> Any:
    """Recovery strategy for network operations."""
    if error.status_code == 429:  # Too Many Requests
        time.sleep(5)  # Wait before retrying
        raise error  # Will be retried
    if error.status_code in [502, 503, 504]:  # Server errors
        raise error  # Will be retried
    # Client errors (4xx) - don't retry
    raise error


def timeout_operation_recovery(error: CustomTimeoutError) -> Any:
    """Recovery strategy for timeout operations."""
    if error.timeout_duration and error.timeout_duration < 30:
        # Increase timeout for retry
        raise CustomTimeoutError(
            error.message,
            timeout_duration=error.timeout_duration * 2,
            error_code="TIMEOUT_RECOVERY",
        )
    # Already tried with extended timeout
    raise error


# Register default recovery strategies
error_recovery_manager.register_recovery_strategy(
    FileOperationError, file_operation_recovery
)
error_recovery_manager.register_recovery_strategy(
    NetworkError, network_operation_recovery
)
error_recovery_manager.register_recovery_strategy(
    CustomTimeoutError, timeout_operation_recovery
)


class ErrorHealthMonitor:
    """Monitor error patterns and system health."""

    def __init__(self, window_size: int = 100):
        if window_size < 1:
            raise ValueError("window_size must be at least 1")

        self.window_size = window_size
        self.error_history = []
        self.error_counts = {}
        self.start_time = datetime.now()

    def record_error(self, error: Exception, context: Dict[str, Any]):
        """Record an error occurrence."""
        error_info = {
            "timestamp": datetime.now(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
        }

        self.error_history.append(error_info)

        # Maintain window size
        if len(self.error_history) > self.window_size:
            self.error_history.pop(0)

        # Update counts
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def get_error_rate(self, time_window_minutes: int = 5) -> float:
        """Get error rate within a time window."""
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_errors = [e for e in self.error_history if e["timestamp"] > cutoff_time]

        # Calculate rate per minute
        return len(recent_errors) / time_window_minutes

    def get_most_common_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most common error types."""
        sorted_errors = sorted(
            self.error_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"error_type": error_type, "count": count}
            for error_type, count in sorted_errors[:limit]
        ]

    def is_system_healthy(self) -> bool:
        """Check if system is healthy based on error patterns."""
        error_rate = self.get_error_rate()

        # System is unhealthy if error rate exceeds threshold
        if error_rate > 10:  # More than 10 errors per minute
            return False

        # Check for cascading failures
        recent_errors = [
            e
            for e in self.error_history
            if e["timestamp"] > datetime.now() - timedelta(minutes=2)
        ]

        if len(recent_errors) > 20:  # Too many errors in short time
            return False

        return True

    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        uptime = datetime.now() - self.start_time

        return {
            "system_healthy": self.is_system_healthy(),
            "uptime_seconds": uptime.total_seconds(),
            "total_errors": len(self.error_history),
            "error_rate_per_minute": self.get_error_rate(),
            "most_common_errors": self.get_most_common_errors(),
            "recent_error_trends": self._analyze_error_trends(),
        }

    def _analyze_error_trends(self) -> Dict[str, Any]:
        """Analyze error trends over time."""
        if len(self.error_history) < 10:
            return {"trend": "insufficient_data"}

        # Compare first and second half of error history by time periods
        mid_point = len(self.error_history) // 2
        first_half = self.error_history[:mid_point]
        second_half = self.error_history[mid_point:]

        # Calculate time duration for each half
        if not first_half or not second_half:
            return {"trend": "insufficient_data"}

        first_duration = (
            first_half[-1]["timestamp"] - first_half[0]["timestamp"]
        ).total_seconds()
        second_duration = (
            second_half[-1]["timestamp"] - second_half[0]["timestamp"]
        ).total_seconds()

        # Avoid division by zero
        if first_duration == 0 or second_duration == 0:
            return {"trend": "insufficient_time_data"}

        # Calculate error rates (errors per second)
        first_half_rate = len(first_half) / first_duration
        second_half_rate = len(second_half) / second_duration

        # Handle edge case where first half rate is 0
        if first_half_rate == 0:
            if second_half_rate > 0:
                return {"trend": "increasing", "severity": "high"}
            return {"trend": "stable", "severity": "normal"}

        ratio = second_half_rate / first_half_rate

        if ratio > 1.5:
            return {"trend": "increasing", "severity": "high"}
        if ratio > 1.2:
            return {"trend": "increasing", "severity": "moderate"}
        if ratio < 0.8:
            return {"trend": "decreasing", "severity": "good"}
        return {"trend": "stable", "severity": "normal"}


# Global health monitor
health_monitor = ErrorHealthMonitor()


def monitor_errors(func: Callable) -> Callable:
    """Decorator to monitor function errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = create_error_context(
                f"{func.__name__}_monitor",
                args=str(args)[:100],  # Truncate for logging
                kwargs=str(kwargs)[:100],
            )
            health_monitor.record_error(e, context)
            raise

    return wrapper


# Async versions of decorators
async def async_with_retry(
    config: Optional[RetryConfig] = None,
    recovery_manager: Optional[ErrorRecoveryManager] = None,
):
    """Async version of retry decorator."""
    if config is None:
        config = RetryConfig()

    if recovery_manager is None:
        recovery_manager = error_recovery_manager

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this exception is retryable
                    if not any(
                        isinstance(e, exc_type)
                        for exc_type in config.retryable_exceptions
                    ):
                        context = create_error_context(
                            f"{func.__name__}_async_retry",
                            attempt=attempt + 1,
                            max_attempts=config.max_attempts,
                        )

                        try:
                            return recovery_manager.attempt_recovery(e, context)
                        except (ValueError, TypeError, AttributeError):
                            raise e from None
                        except Exception as recovery_error:
                            logging.error(
                                "Async recovery failed for %s: %s",
                                func.__name__,
                                recovery_error,
                            )
                            raise e from None

                    # Calculate delay for next attempt
                    if attempt < config.max_attempts - 1:
                        delay = min(
                            config.base_delay * (config.exponential_base**attempt),
                            config.max_delay,
                        )

                        if config.jitter:
                            delay *= 0.5 + secrets.SystemRandom().random() * 0.5

                        await asyncio.sleep(delay)

            # All attempts failed
            raise last_exception

        return wrapper

    return decorator
