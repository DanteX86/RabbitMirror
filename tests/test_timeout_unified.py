#!/usr/bin/env python3
import os
import sys
import time
from typing import List

import pytest

# Ensure project root is on sys.path for direct test execution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from rabbitmirror.exceptions import CustomTimeoutError  # noqa: E402
from rabbitmirror.timeout import TimeoutToken, run_with_timeout, timeout  # noqa: E402


class TestUnifiedTimeoutThreadMode:
    def test_cooperative_completion(self):
        def work(n: int, timeout_token: TimeoutToken):
            total = 0
            for i in range(n):
                # Check token cooperatively
                timeout_token.raise_if_cancelled()
                total += i
                time.sleep(0.005)
            return total

        result = run_with_timeout(work, 0.5, 50, mode="thread")
        assert isinstance(result, int)

    def test_cooperative_timeout(self):
        def work(timeout_token: TimeoutToken):
            # Busy loop, but still checks token
            while True:
                timeout_token.raise_if_cancelled()
                time.sleep(0.01)

        with pytest.raises(CustomTimeoutError) as exc:
            run_with_timeout(work, 0.1, mode="thread")
        assert "THREAD_TIMEOUT" in str(exc.value)

    def test_decorator_thread_mode(self):
        @timeout(0.2, mode="thread")
        def fast_fn(timeout_token: TimeoutToken):
            time.sleep(0.05)
            return "ok"

        assert fast_fn() == "ok"


class TestUnifiedTimeoutProcessMode:
    def test_process_completion(self):
        def compute(x: int) -> int:
            return x * x

        assert run_with_timeout(compute, 1.0, 5, mode="process") == 25

    def test_process_timeout(self):
        def hang():
            time.sleep(5)

        start = time.time()
        with pytest.raises(CustomTimeoutError) as exc:
            run_with_timeout(hang, 0.2, mode="process")
        elapsed = time.time() - start
        assert elapsed < 1.5  # should return promptly
        assert "PROCESS_TIMEOUT" in str(exc.value)

    def test_process_exception_propagation(self):
        def boom():
            raise ValueError("boom")

        with pytest.raises(ValueError):
            run_with_timeout(boom, 1.0, mode="process")

    def test_decorator_process_mode(self):
        @timeout(0.5, mode="process")
        def slow_ok():
            time.sleep(0.1)
            return "ok"

        assert slow_ok() == "ok"


class TestThreadModeWithoutToken:
    def test_runs_without_token_param(self):
        def f(x: int) -> int:
            time.sleep(0.05)
            return x + 1

        assert run_with_timeout(f, 0.5, 1, mode="thread") == 2


class TestEdgeCases:
    def test_zero_timeout_thread(self):
        def quick(timeout_token: TimeoutToken):
            return 123

        assert run_with_timeout(quick, 0.0, mode="thread") == 123

    def test_zero_timeout_process(self):
        def quick():
            return 456

        assert run_with_timeout(quick, 0.0, mode="process") == 456

    def test_negative_timeout_raises(self):
        def noop():
            return None

        with pytest.raises(ValueError):
            run_with_timeout(noop, -1.0)
