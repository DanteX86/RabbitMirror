#!/usr/bin/env python3
"""
Integration tests to verify timeout decorator behavior within the benchmark framework
without running long or heavy benchmarks. We validate that benchmark utilities can
execute functions decorated with timeouts and correctly propagate results and errors.
"""
import time

import pytest

from benchmarks.utils import PerformanceMonitor
from rabbitmirror.exceptions import CustomTimeoutError
from rabbitmirror.timeout import TimeoutToken, timeout


class TestTimeoutWithBenchmarkFramework:
    def test_monitor_with_thread_timeout_success(self):
        monitor = PerformanceMonitor()
        monitor.start()

        @timeout(0.5, mode="thread")
        def quick(timeout_token: TimeoutToken):
            time.sleep(0.05)
            timeout_token.raise_if_cancelled()
            return "ok"

        val = quick()
        metrics = monitor.stop()

        assert val == "ok"
        assert "total_time" in metrics and metrics["total_time"] >= 0

    def test_monitor_with_thread_timeout_exceeded(self):
        monitor = PerformanceMonitor()
        monitor.start()

        @timeout(0.05, mode="thread")
        def slow(timeout_token: TimeoutToken):
            start = time.time()
            while time.time() - start < 1.0:
                timeout_token.raise_if_cancelled()
                time.sleep(0.01)

        with pytest.raises(CustomTimeoutError):
            slow()
        # Even after failure, stop the monitor to get metrics
        metrics = monitor.stop()
        assert "total_time" in metrics

    def test_monitor_with_process_timeout_success(self):
        monitor = PerformanceMonitor()
        monitor.start()

        @timeout(1.0, mode="process")
        def compute(x, y):
            return x + y

        assert compute(2, 3) == 5
        metrics = monitor.stop()
        assert metrics["total_time"] >= 0

    def test_monitor_with_process_timeout_exceeded(self):
        monitor = PerformanceMonitor()
        monitor.start()

        @timeout(0.05, mode="process")
        def hang():
            time.sleep(0.5)

        with pytest.raises(CustomTimeoutError):
            hang()
        metrics = monitor.stop()
        assert metrics["total_time"] >= 0
