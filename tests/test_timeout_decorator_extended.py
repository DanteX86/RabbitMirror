#!/usr/bin/env python3
import threading
import time
from unittest.mock import patch

import pytest

from rabbitmirror.exceptions import CustomTimeoutError
from rabbitmirror.timeout import TimeoutToken, run_with_timeout, timeout


class TestTimeoutDecoratorMainThreadSignalMode:
    def test_signal_mode_main_thread_success(self, monkeypatch):
        # Ensure we simulate availability of signal mode
        monkeypatch.setattr("rabbitmirror.timeout._can_use_signal_mode", lambda: True)

        # Patch signal functions to be harmless and observable
        with (
            patch("rabbitmirror.timeout.signal.signal") as mock_signal,
            patch("rabbitmirror.timeout.signal.setitimer") as mock_setitimer,
            patch("rabbitmirror.timeout.signal.getsignal") as mock_getsignal,
        ):
            mock_getsignal.return_value = None

            @timeout(1.0, mode="signal")
            def fast():
                return "ok"

            assert fast() == "ok"
            # Verify signal mode was actually used (handlers set, timer armed)
            assert mock_signal.called
            assert mock_setitimer.called

    def test_signal_mode_timeout_raises(self, monkeypatch):
        # Force signal mode path
        monkeypatch.setattr("rabbitmirror.timeout._can_use_signal_mode", lambda: True)

        # Simulate a timeout by making setitimer raise our timeout error
        def fake_setitimer(_, __):
            raise CustomTimeoutError("simulated alarm", error_code="SIGNAL_TIMEOUT")

        with (
            patch("rabbitmirror.timeout.signal.signal") as mock_signal,
            patch("rabbitmirror.timeout.signal.setitimer", side_effect=fake_setitimer),
            patch("rabbitmirror.timeout.signal.getsignal") as mock_getsignal,
        ):
            mock_getsignal.return_value = None

            @timeout(0.01, mode="signal")
            def slow():
                time.sleep(0.1)

            with pytest.raises(CustomTimeoutError) as exc:
                slow()
            assert "SIGNAL_TIMEOUT" in str(exc.value)


class TestTimeoutDecoratorWorkerThreadContext:
    def test_signal_mode_in_worker_thread_falls_back_to_thread(self):
        # When calling signal mode inside a worker thread, implementation falls back to thread mode.
        result_holder = {}
        exc_holder = {}

        @timeout(0.5, mode="signal")
        def quick(timeout_token: TimeoutToken):
            # Should run cooperatively in thread mode due to fallback
            time.sleep(0.05)
            timeout_token.raise_if_cancelled()
            return "done"

        def runner():
            try:
                result_holder["val"] = quick()
            except Exception as e:  # Capture for assertion in main thread
                exc_holder["err"] = e

        t = threading.Thread(target=runner)
        t.start()
        t.join(timeout=2)

        assert "err" not in exc_holder, f"Unexpected error: {exc_holder['err']}"
        assert result_holder.get("val") == "done"


class TestTimeoutEdgeCases:
    def test_function_completes_before_timeout_thread(self):
        @timeout(0.5, mode="thread")
        def fn(timeout_token: TimeoutToken):
            time.sleep(0.05)
            timeout_token.raise_if_cancelled()
            return 123

        assert fn() == 123

    def test_function_exceeds_timeout_thread(self):
        @timeout(0.05, mode="thread")
        def fn(timeout_token: TimeoutToken):
            # Cooperative loop but exceeds
            start = time.time()
            while time.time() - start < 1.0:
                timeout_token.raise_if_cancelled()
                time.sleep(0.01)

        with pytest.raises(CustomTimeoutError) as exc:
            fn()
        assert "THREAD_TIMEOUT" in str(exc.value)

    def test_nested_timeout_decorators_outer_shorter(self):
        # Outer should fire first
        def base():
            time.sleep(0.2)
            return "done"

        wrapped = timeout(0.5, mode="thread")(base)
        wrapped = timeout(0.05, mode="thread")(wrapped)

        with pytest.raises(CustomTimeoutError) as exc:
            wrapped()
        assert "THREAD_TIMEOUT" in str(exc.value)

    def test_nested_timeout_decorators_inner_shorter(self):
        # Inner should raise and propagate
        @timeout(0.5, mode="thread")
        @timeout(0.05, mode="thread")
        def fn(timeout_token: TimeoutToken):
            start = time.time()
            while time.time() - start < 1.0:
                timeout_token.raise_if_cancelled()
                time.sleep(0.01)

        with pytest.raises(CustomTimeoutError) as exc:
            fn()
        assert "THREAD_TIMEOUT" in str(exc.value)

    def test_exception_handling_within_timed_function_thread(self):
        @timeout(0.5, mode="thread")
        def boom():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            boom()

    def test_exception_handling_within_timed_function_process(self):
        @timeout(0.5, mode="process")
        def boom():
            raise KeyError("nope")

        with pytest.raises(KeyError):
            boom()


class TestDecoratorProcessModeBasics:
    def test_process_completes_before_timeout(self):
        @timeout(1.0, mode="process")
        def square(x):
            return x * x

        assert square(4) == 16

    def test_process_exceeds_timeout(self):
        @timeout(0.05, mode="process")
        def slow():
            time.sleep(0.5)

        start = time.time()
        with pytest.raises(CustomTimeoutError) as exc:
            slow()
        elapsed = time.time() - start
        assert elapsed < 1.0
        assert "PROCESS_TIMEOUT" in str(exc.value)
