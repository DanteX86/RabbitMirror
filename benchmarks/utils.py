"""
Performance benchmarking utilities for RabbitMirror.
"""

import time
import psutil
import gc
import os
import functools
from typing import Dict, Any, List, Callable, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json
import tempfile
import random
import string
from memory_profiler import profile
import matplotlib.pyplot as plt
import numpy as np


class PerformanceMonitor:
    """Monitor performance metrics during execution."""
    
    def __init__(self):
        self.metrics = []
        self.start_time = None
        self.process = psutil.Process()
        
    def start(self):
        """Start monitoring."""
        self.start_time = time.time()
        self.metrics = []
        gc.collect()  # Clean up before starting
        
    def record(self, label: str = None):
        """Record current metrics."""
        if self.start_time is None:
            raise RuntimeError("Monitor not started")
            
        current_time = time.time()
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()
        
        metric = {
            'timestamp': current_time,
            'elapsed': current_time - self.start_time,
            'label': label or f'checkpoint_{len(self.metrics)}',
            'memory_rss': memory_info.rss,
            'memory_vms': memory_info.vms,
            'cpu_percent': cpu_percent,
            'num_threads': self.process.num_threads(),
        }
        
        self.metrics.append(metric)
        return metric
        
    def stop(self):
        """Stop monitoring and return final metrics."""
        if self.start_time is None:
            raise RuntimeError("Monitor not started")
            
        self.record('final')
        total_time = time.time() - self.start_time
        
        return {
            'total_time': total_time,
            'peak_memory': max(m['memory_rss'] for m in self.metrics),
            'avg_cpu': np.mean([m['cpu_percent'] for m in self.metrics]),
            'metrics': self.metrics
        }


class BenchmarkDataGenerator:
    """Generate test data for benchmarking."""
    
    @staticmethod
    def generate_html_file(num_entries: int, file_path: Optional[str] = None) -> str:
        """Generate HTML file with specified number of entries."""
        if file_path is None:
            fd, file_path = tempfile.mkstemp(suffix='.html')
            with os.fdopen(fd, 'w') as f:
                pass
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>YouTube Watch History</title>
</head>
<body>
    <h1>YouTube Watch History</h1>
''')
            
            for i in range(num_entries):
                title = f"Video {i}: {BenchmarkDataGenerator._random_title()}"
                video_id = BenchmarkDataGenerator._random_video_id()
                timestamp = BenchmarkDataGenerator._random_timestamp()
                
                f.write(f'''
    <div class="content-cell">
        <a href="https://www.youtube.com/watch?v={video_id}">{title}</a>
        <div class="mdl-typography--caption">{timestamp}</div>
    </div>
''')
            
            f.write('</body></html>')
        
        return file_path
    
    @staticmethod
    def generate_json_data(num_entries: int) -> Dict[str, Any]:
        """Generate JSON data with specified number of entries."""
        entries = []
        for i in range(num_entries):
            entries.append({
                'title': f"Video {i}: {BenchmarkDataGenerator._random_title()}",
                'url': f"https://www.youtube.com/watch?v={BenchmarkDataGenerator._random_video_id()}",
                'timestamp': BenchmarkDataGenerator._random_iso_timestamp()
            })
        
        return {
            'metadata': {
                'source': 'Benchmark Data',
                'generated_at': datetime.now().isoformat(),
                'total_entries': num_entries,
            },
            'entries': entries
        }
    
    @staticmethod
    def _random_title() -> str:
        """Generate random video title."""
        topics = [
            'Python Tutorial', 'Machine Learning', 'Data Science', 'Web Development',
            'JavaScript Guide', 'React Tutorial', 'Docker Container', 'AWS Cloud',
            'Database Design', 'API Development', 'Security Tips', 'Performance Optimization'
        ]
        return random.choice(topics) + ' ' + ''.join(random.choices(string.ascii_letters, k=10))
    
    @staticmethod
    def _random_video_id() -> str:
        """Generate random YouTube video ID."""
        return ''.join(random.choices(string.ascii_letters + string.digits + '_-', k=11))
    
    @staticmethod
    def _random_timestamp() -> str:
        """Generate random timestamp in YouTube format."""
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month = random.choice(months)
        day = random.randint(1, 28)
        year = random.randint(2020, 2023)
        hour = random.randint(1, 12)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        ampm = random.choice(['AM', 'PM'])
        
        return f"{month} {day}, {year}, {hour}:{minute:02d}:{second:02d} {ampm}"
    
    @staticmethod
    def _random_iso_timestamp() -> str:
        """Generate random ISO timestamp."""
        year = random.randint(2020, 2023)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        return f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"


class BenchmarkReporter:
    """Generate benchmark reports."""
    
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_report(self, results: Dict[str, Any], title: str = "Benchmark Report"):
        """Generate comprehensive benchmark report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"benchmark_report_{timestamp}.json"
        
        # Save raw results
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate HTML report
        html_file = self.output_dir / f"benchmark_report_{timestamp}.html"
        self._generate_html_report(results, html_file, title)
        
        # Generate charts
        self._generate_charts(results, timestamp)
        
        return {
            'report_file': str(report_file),
            'html_file': str(html_file),
            'timestamp': timestamp
        }
    
    def _generate_html_report(self, results: Dict[str, Any], file_path: Path, title: str):
        """Generate HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
        .chart {{ margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Summary</h2>
    <div class="metric">
        <strong>Total Benchmarks:</strong> {len(results)}
    </div>
    
    <h2>Results</h2>
    <table>
        <tr>
            <th>Benchmark</th>
            <th>Time (seconds)</th>
            <th>Memory (MB)</th>
            <th>CPU %</th>
        </tr>
"""
        
        for name, result in results.items():
            if isinstance(result, dict) and 'total_time' in result:
                time_val = f"{result['total_time']:.4f}"
                memory_val = f"{result['peak_memory'] / 1024 / 1024:.2f}"
                cpu_val = f"{result.get('avg_cpu', 0):.2f}"
                
                html_content += f"""
        <tr>
            <td>{name}</td>
            <td>{time_val}</td>
            <td>{memory_val}</td>
            <td>{cpu_val}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(file_path, 'w') as f:
            f.write(html_content)
    
    def _generate_charts(self, results: Dict[str, Any], timestamp: str):
        """Generate performance charts."""
        try:
            # Extract metrics for plotting
            names = []
            times = []
            memories = []
            
            for name, result in results.items():
                if isinstance(result, dict) and 'total_time' in result:
                    names.append(name)
                    times.append(result['total_time'])
                    memories.append(result['peak_memory'] / 1024 / 1024)
            
            if not names:
                return
            
            # Create time comparison chart
            plt.figure(figsize=(12, 6))
            plt.subplot(1, 2, 1)
            plt.bar(names, times)
            plt.title('Execution Time Comparison')
            plt.xlabel('Benchmark')
            plt.ylabel('Time (seconds)')
            plt.xticks(rotation=45)
            
            # Create memory comparison chart
            plt.subplot(1, 2, 2)
            plt.bar(names, memories)
            plt.title('Peak Memory Usage Comparison')
            plt.xlabel('Benchmark')
            plt.ylabel('Memory (MB)')
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig(self.output_dir / f"benchmark_charts_{timestamp}.png", dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"Warning: Could not generate charts: {e}")


def benchmark_function(name: str = None, warmup: int = 1, iterations: int = 5):
    """Decorator to benchmark a function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            monitor = PerformanceMonitor()
            
            # Warmup runs
            for _ in range(warmup):
                func(*args, **kwargs)
            
            # Benchmark runs
            results = []
            for i in range(iterations):
                monitor.start()
                result = func(*args, **kwargs)
                metrics = monitor.stop()
                results.append(metrics)
            
            # Calculate statistics
            times = [r['total_time'] for r in results]
            memories = [r['peak_memory'] for r in results]
            
            stats = {
                'function': func_name,
                'iterations': iterations,
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'min_time': np.min(times),
                'max_time': np.max(times),
                'avg_memory': np.mean(memories),
                'peak_memory': np.max(memories),
                'individual_results': results
            }
            
            print(f"\nBenchmark: {func_name}")
            print(f"Average time: {stats['avg_time']:.4f}s ± {stats['std_time']:.4f}s")
            print(f"Peak memory: {stats['peak_memory'] / 1024 / 1024:.2f}MB")
            
            return result, stats
        
        return wrapper
    return decorator


def memory_usage_profile(func: Callable) -> Callable:
    """Decorator to profile memory usage."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from memory_profiler import profile as mem_profile
        return mem_profile(func)(*args, **kwargs)
    return wrapper


def compare_implementations(*implementations: Tuple[str, Callable], 
                          test_data: Any = None, 
                          iterations: int = 5) -> Dict[str, Any]:
    """Compare multiple implementations."""
    results = {}
    
    for name, impl in implementations:
        monitor = PerformanceMonitor()
        times = []
        memories = []
        
        for _ in range(iterations):
            monitor.start()
            if test_data is not None:
                impl(test_data)
            else:
                impl()
            metrics = monitor.stop()
            times.append(metrics['total_time'])
            memories.append(metrics['peak_memory'])
        
        results[name] = {
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'min_time': np.min(times),
            'max_time': np.max(times),
            'avg_memory': np.mean(memories),
            'peak_memory': np.max(memories),
            'times': times,
            'memories': memories
        }
    
    return results


def scalability_test(func: Callable, 
                    data_sizes: List[int], 
                    data_generator: Callable,
                    iterations: int = 3) -> Dict[str, Any]:
    """Test scalability across different data sizes."""
    results = {}
    
    for size in data_sizes:
        print(f"Testing with {size} entries...")
        test_data = data_generator(size)
        
        monitor = PerformanceMonitor()
        times = []
        memories = []
        
        for _ in range(iterations):
            monitor.start()
            func(test_data)
            metrics = monitor.stop()
            times.append(metrics['total_time'])
            memories.append(metrics['peak_memory'])
        
        results[f'size_{size}'] = {
            'data_size': size,
            'avg_time': np.mean(times),
            'std_time': np.std(times),
            'avg_memory': np.mean(memories),
            'peak_memory': np.max(memories),
        }
    
    return results
