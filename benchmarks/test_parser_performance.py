"""
Performance benchmarks for the parser module.
"""

import os
import tempfile

import numpy as np
import pytest
from utils import (
    BenchmarkDataGenerator,
    BenchmarkReporter,
    PerformanceMonitor,
    scalability_test,
)

from rabbitmirror.parser import HistoryParser


class TestParserPerformance:
    """Test parser performance with various data sizes and conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = BenchmarkDataGenerator()
        self.reporter = BenchmarkReporter("benchmark_results/parser")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_scalability(self):
        """Test parser performance across different data sizes."""
        data_sizes = [100, 500, 1000, 5000, 10000]

        def parse_html_file(size):
            file_path = self.generator.generate_html_file(size)
            try:
                parser = HistoryParser(file_path)
                return parser.parse()
            finally:
                os.unlink(file_path)

        results = scalability_test(
            parse_html_file,
            data_sizes,
            lambda size: size,  # Pass size directly
            iterations=3,
        )

        # Analyze results
        self._analyze_scalability_results(results, "Parse Scalability")

        # Generate report
        self.reporter.generate_report(results, "Parser Scalability Test")

    def test_parse_encoding_performance(self):
        """Test parser performance with different encodings."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        num_entries = 1000

        results = {}

        for encoding in encodings:
            file_path = self.generator.generate_html_file(num_entries)

            # Re-write file with specific encoding
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)

            try:
                monitor = PerformanceMonitor()
                times = []
                memories = []

                for _ in range(5):
                    monitor.start()
                    parser = HistoryParser(file_path)
                    parser.parse()
                    metrics = monitor.stop()
                    times.append(metrics["total_time"])
                    memories.append(metrics["peak_memory"])

                results[f"encoding_{encoding}"] = {
                    "avg_time": np.mean(times),
                    "std_time": np.std(times),
                    "avg_memory": np.mean(memories),
                    "peak_memory": np.max(memories),
                }

            finally:
                os.unlink(file_path)

        self.reporter.generate_report(results, "Parser Encoding Performance")

    def test_parse_error_handling_performance(self):
        """Test parser performance with error conditions."""
        num_entries = 1000

        # Test with various error conditions
        error_conditions = [
            ("valid_file", lambda: self.generator.generate_html_file(num_entries)),
            ("malformed_html", lambda: self._create_malformed_html(num_entries)),
            (
                "invalid_timestamps",
                lambda: self._create_invalid_timestamps(num_entries),
            ),
            ("missing_fields", lambda: self._create_missing_fields(num_entries)),
        ]

        results = {}

        for condition_name, file_generator in error_conditions:
            file_path = file_generator()

            try:
                monitor = PerformanceMonitor()
                times = []
                memories = []
                errors = 0

                for _ in range(5):
                    try:
                        monitor.start()
                        parser = HistoryParser(file_path)
                        parser.parse()
                        metrics = monitor.stop()
                        times.append(metrics["total_time"])
                        memories.append(metrics["peak_memory"])
                    except Exception:
                        errors += 1
                        if monitor.start_time:
                            metrics = monitor.stop()
                            times.append(metrics["total_time"])
                            memories.append(metrics["peak_memory"])

                if times:  # Only record if we have measurements
                    results[condition_name] = {
                        "avg_time": np.mean(times),
                        "std_time": np.std(times),
                        "avg_memory": np.mean(memories),
                        "peak_memory": np.max(memories),
                        "error_count": errors,
                        "success_rate": (5 - errors) / 5,
                    }

            finally:
                if os.path.exists(file_path):
                    os.unlink(file_path)

        self.reporter.generate_report(results, "Parser Error Handling Performance")

    def test_parse_memory_efficiency(self):
        """Test parser memory efficiency with large files."""
        data_sizes = [1000, 5000, 10000, 20000]

        results = {}

        for size in data_sizes:
            file_path = self.generator.generate_html_file(size)

            try:
                # Monitor memory usage throughout parsing
                monitor = PerformanceMonitor()
                monitor.start()

                parser = HistoryParser(file_path)
                monitor.record("parser_created")

                data = parser.parse()
                monitor.record("parsing_complete")

                # Force garbage collection
                import gc

                gc.collect()
                monitor.record("gc_complete")

                final_metrics = monitor.stop()

                # Handle both dict and list return types
                if isinstance(data, dict):
                    parsed_entries = len(data.get("entries", []))
                elif isinstance(data, list):
                    parsed_entries = len(data)
                else:
                    parsed_entries = 0

                results[f"size_{size}"] = {
                    "data_size": size,
                    "total_time": final_metrics["total_time"],
                    "peak_memory": final_metrics["peak_memory"],
                    "avg_cpu": final_metrics["avg_cpu"],
                    "parsed_entries": parsed_entries,
                    "memory_per_entry": final_metrics["peak_memory"] / size,
                    "time_per_entry": final_metrics["total_time"] / size,
                    "detailed_metrics": final_metrics["metrics"],
                }

            finally:
                os.unlink(file_path)

        self.reporter.generate_report(results, "Parser Memory Efficiency")

    def test_concurrent_parsing_performance(self):
        """Test parser performance with concurrent parsing."""
        import concurrent.futures

        num_files = 5
        entries_per_file = 1000

        # Create test files
        test_files = []
        for i in range(num_files):
            file_path = self.generator.generate_html_file(entries_per_file)
            test_files.append(file_path)

        try:
            # Sequential parsing
            monitor = PerformanceMonitor()
            monitor.start()

            sequential_results = []
            for file_path in test_files:
                parser = HistoryParser(file_path)
                result = parser.parse()
                sequential_results.append(result)

            sequential_metrics = monitor.stop()

            # Concurrent parsing
            def parse_file(file_path):
                parser = HistoryParser(file_path)
                return parser.parse()

            monitor = PerformanceMonitor()
            monitor.start()

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                concurrent_results = list(executor.map(parse_file, test_files))

            concurrent_metrics = monitor.stop()

            results = {
                "sequential_parsing": {
                    "total_time": sequential_metrics["total_time"],
                    "peak_memory": sequential_metrics["peak_memory"],
                    "avg_cpu": sequential_metrics["avg_cpu"],
                    "files_processed": len(test_files),
                    "total_entries": sum(
                        len(r.get("entries", []))
                        if isinstance(r, dict)
                        else len(r)
                        for r in sequential_results
                    ),
                },
                "concurrent_parsing": {
                    "total_time": concurrent_metrics["total_time"],
                    "peak_memory": concurrent_metrics["peak_memory"],
                    "avg_cpu": concurrent_metrics["avg_cpu"],
                    "files_processed": len(test_files),
                    "total_entries": sum(
                        len(r.get("entries", []))
                        if isinstance(r, dict)
                        else len(r)
                        for r in concurrent_results
                    ),
                    "speedup": sequential_metrics["total_time"]
                    / concurrent_metrics["total_time"],
                },
            }

            self.reporter.generate_report(results, "Parser Concurrent Performance")

        finally:
            for file_path in test_files:
                os.unlink(file_path)

    def _analyze_scalability_results(self, results, title):
        """Analyze scalability results for complexity."""
        sizes = []
        times = []
        memories = []

        for key, result in results.items():
            if key.startswith("size_"):
                size = result["data_size"]
                sizes.append(size)
                times.append(result["avg_time"])
                memories.append(result["avg_memory"])

        # Calculate time complexity (approximate)
        if len(sizes) > 1:
            # Fit polynomial to estimate complexity
            time_poly = np.polyfit(sizes, times, 2)
            memory_poly = np.polyfit(sizes, memories, 2)

            print(f"\n{title} Analysis:")
            print(f"Time complexity coefficients: {time_poly}")
            print(f"Memory complexity coefficients: {memory_poly}")

            # Calculate efficiency metrics
            time_per_entry = [t / s for t, s in zip(times, sizes)]
            memory_per_entry = [m / s for m, s in zip(memories, sizes)]

            print(f"Average time per entry: {np.mean(time_per_entry):.6f}s")
            print(f"Average memory per entry: {np.mean(memory_per_entry):.2f}MB")

    def _create_malformed_html(self, num_entries):
        """Create HTML file with malformed structure."""
        fd, file_path = tempfile.mkstemp(suffix=".html")

        with os.fdopen(fd, "w") as f:
            f.write("<html><body><h1>Malformed HTML</h1>\n")

            for i in range(num_entries):
                # Intentionally create malformed HTML
                if i % 10 == 0:
                    f.write(
                        f'<div class="content-cell"><a href="bad_url">Title {i}</a>\n'
                    )
                elif i % 15 == 0:
                    f.write(
                        f'<div><a href="url">Title {i}</a><div>Bad timestamp</div>\n'
                    )
                else:
                    f.write(
                        f'<div class="content-cell"><a href="url">Title {i}</a>'
                        f'<div class="mdl-typography--caption">Jan 1, 2023</div>'
                        '</div>\n'
                    )

            f.write("</body></html>")

        return file_path

    def _create_invalid_timestamps(self, num_entries):
        """Create HTML file with invalid timestamps."""
        fd, file_path = tempfile.mkstemp(suffix=".html")

        with os.fdopen(fd, "w") as f:
            f.write("<html><body><h1>Invalid Timestamps</h1>\n")

            for i in range(num_entries):
                # Create various invalid timestamp formats
                invalid_timestamps = [
                    "Invalid Date",
                    "2023-13-45",
                    "Not a date",
                    "32 Feb 2023",
                    "",
                    "null",
                ]
                timestamp = invalid_timestamps[i % len(invalid_timestamps)]

                f.write(
                    f'<div class="content-cell"><a href="url">Title {i}</a>'
                    f'<div class="mdl-typography--caption">{timestamp}</div></div>\n'
                )

            f.write("</body></html>")

        return file_path

    def _create_missing_fields(self, num_entries):
        """Create HTML file with missing fields."""
        fd, file_path = tempfile.mkstemp(suffix=".html")

        with os.fdopen(fd, "w") as f:
            f.write("<html><body><h1>Missing Fields</h1>\n")

            for i in range(num_entries):
                if i % 3 == 0:
                    # Missing title
                    f.write(
                        '<div class="content-cell"><a href="url"></a>'
                        '<div class="mdl-typography--caption">Jan 1, 2023</div></div>\n'
                    )
                elif i % 5 == 0:
                    # Missing URL
                    f.write(
                        f'<div class="content-cell"><a>Title {i}</a>'
                        '<div class="mdl-typography--caption">Jan 1, 2023</div></div>\n'
                    )
                elif i % 7 == 0:
                    # Missing timestamp
                    f.write(
                        f'<div class="content-cell"><a href="url">Title {i}</a></div>\n'
                    )
                else:
                    # Valid entry
                    f.write(
                        f'<div class="content-cell"><a href="url">Title {i}</a>'
                        '<div class="mdl-typography--caption">Jan 1, 2023</div></div>\n'
                    )

            f.write("</body></html>")

        return file_path


@pytest.mark.benchmark
def test_parser_benchmark_suite():
    """Run comprehensive parser benchmark suite."""
    test_instance = TestParserPerformance()
    test_instance.setup_method()

    try:
        # Run all benchmark tests
        test_instance.test_parse_scalability()
        test_instance.test_parse_encoding_performance()
        test_instance.test_parse_error_handling_performance()
        test_instance.test_parse_memory_efficiency()
        test_instance.test_concurrent_parsing_performance()

        print("Parser benchmark suite completed successfully!")

    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    test_parser_benchmark_suite()
