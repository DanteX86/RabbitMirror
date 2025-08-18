#!/usr/bin/env python3
import os
import sys
import threading
import time

import pytest

# Avoid importing the package test conftest; add project root directly
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from rabbitmirror.exceptions import CustomTimeoutError
from rabbitmirror.timeout import TimeoutToken, run_with_timeout, timeout


def in_main_thread():
    import threading as _th

    return _th.current_thread() is _th.main_thread()


@pytest.mark.parametrize(
    "mode", ["auto", "signal"]
)  # signal will fall back in workers/non-POSIX
def test_quick_function_completes(mode):
    def quick():
        return "ok"

    assert run_with_timeout(quick, 0.2, mode=mode) == "ok"


def test_signal_mode_timeout_in_main_thread_or_fallback():
    def hang():
        time.sleep(2)

    start = time.time()
    try:
        run_with_timeout(hang, 0.1, mode="signal")
        if not in_main_thread():
            # In non-main thread, signal mode should have fallen back to thread mode and not necessarily timeout here
            # But since this test runs in main thread under pytest, we expect a timeout.
            pass
        pytest.fail("Expected timeout did not occur")
    except CustomTimeoutError as e:
        # Either SIGNAL_TIMEOUT or THREAD_TIMEOUT depending on environment
        msg = str(e)
        assert ("SIGNAL_TIMEOUT" in msg) or ("THREAD_TIMEOUT" in msg)
    finally:
        elapsed = time.time() - start
        assert elapsed < 1.5


def test_auto_mode_uses_signal_in_main_thread_when_available():
    # This test checks behavior by ensuring a timeout occurs quickly in auto mode.
    def hang():
        time.sleep(2)

    start = time.time()
    with pytest.raises(CustomTimeoutError):
        run_with_timeout(hang, 0.1, mode="auto")
    assert time.time() - start < 1.5


def test_decorator_auto_mode():
    @timeout(0.2, mode="auto")
    def short(timeout_token: TimeoutToken = None):
        time.sleep(0.05)
        return "done"

    assert short() == "done"
