"""
Performance benchmarks for the clustering module.
"""

import pytest
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.cluster import DBSCAN
import time

from utils import (
    PerformanceMonitor,
    BenchmarkDataGenerator,
    BenchmarkReporter,
    benchmark_function,
    scalability_test,
    compare_implementations
)

from rabbitmirror.cluster_engine import ClusterEngine
from rabbitmirror.exceptions import ClusteringError


class TestClusteringPerformance:
    """Test clustering performance with various data sizes and parameters."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = BenchmarkDataGenerator()
        self.reporter = BenchmarkReporter("benchmark_results/clustering")
        
    def test_clustering_scalability(self):
        """Test clustering performance across different data sizes."""
        data_sizes = [100, 500, 1000, 2000, 5000]
        
        def cluster_data(size):
            data = self.generator.generate_json_data(size)
            engine = ClusterEngine(eps=0.3, min_samples=5)
            return engine.cluster_videos(data['entries'])
        
        results = scalability_test(
            cluster_data,
            data_sizes,
            lambda size: size,
            iterations=3
        )
        
        self._analyze_clustering_scalability(results)
        self.reporter.generate_report(results, "Clustering Scalability Test")
    
    def test_clustering_parameter_optimization(self):
        """Test clustering performance with different parameters."""
        test_data = self.generator.generate_json_data(1000)
        
        # Test different eps values
        eps_values = [0.1, 0.3, 0.5, 0.7, 0.9]
        min_samples_values = [3, 5, 10, 15, 20]
        
        results = {}
        
        for eps in eps_values:
            for min_samples in min_samples_values:
                param_key = f"eps_{eps}_min_samples_{min_samples}"
                
                monitor = PerformanceMonitor()
                times = []
                memories = []
                cluster_counts = []
                
                for _ in range(3):
                    try:
                        monitor.start()
                        engine = ClusterEngine(eps=eps, min_samples=min_samples)
                        result = engine.cluster_videos(test_data['entries'])
                        metrics = monitor.stop()
                        
                        times.append(metrics['total_time'])
                        memories.append(metrics['peak_memory'])
                        cluster_counts.append(result['cluster_info']['total_clusters'])
                    except Exception as e:
                        print(f"Error with parameters eps={eps}, min_samples={min_samples}: {e}")
                        continue
                
                if times:
                    results[param_key] = {
                        'eps': eps,
                        'min_samples': min_samples,
                        'avg_time': np.mean(times),
                        'std_time': np.std(times),
                        'avg_memory': np.mean(memories),
                        'peak_memory': np.max(memories),
                        'avg_clusters': np.mean(cluster_counts),
                        'std_clusters': np.std(cluster_counts)
                    }
        
        self.reporter.generate_report(results, "Clustering Parameter Optimization")
    
    def test_clustering_algorithms_comparison(self):
        """Compare different clustering approaches."""
        test_data = self.generator.generate_json_data(1000)
        
        # Test different clustering strategies
        implementations = [
            ("DBSCAN_default", lambda data: self._cluster_dbscan(data, 0.3, 5)),
            ("DBSCAN_tight", lambda data: self._cluster_dbscan(data, 0.1, 3)),
            ("DBSCAN_loose", lambda data: self._cluster_dbscan(data, 0.7, 10)),
        ]
        
        results = compare_implementations(
            *implementations,
            test_data=test_data['entries'],
            iterations=5
        )
        
        # Add clustering quality metrics
        for impl_name, impl_func in implementations:
            try:
                cluster_result = impl_func(test_data['entries'])
                results[impl_name].update({
                    'total_clusters': cluster_result['cluster_info']['total_clusters'],
                    'noise_points': cluster_result['cluster_info']['noise_points'],
                    'clustered_entries': cluster_result['cluster_info']['total_entries'] - cluster_result['cluster_info']['noise_points'],
                    'clustering_ratio': (cluster_result['cluster_info']['total_entries'] - cluster_result['cluster_info']['noise_points']) / cluster_result['cluster_info']['total_entries']
                })
            except Exception as e:
                print(f"Error getting quality metrics for {impl_name}: {e}")
        
        self.reporter.generate_report(results, "Clustering Algorithms Comparison")
    
    def test_clustering_memory_efficiency(self):
        """Test clustering memory efficiency with large datasets."""
        data_sizes = [500, 1000, 2000, 5000, 10000]
        
        results = {}
        
        for size in data_sizes:
            test_data = self.generator.generate_json_data(size)
            
            monitor = PerformanceMonitor()
            monitor.start()
            
            engine = ClusterEngine(eps=0.3, min_samples=5)
            monitor.record('engine_created')
            
            cluster_result = engine.cluster_videos(test_data['entries'])
            monitor.record('clustering_complete')
            
            # Force garbage collection
            import gc
            gc.collect()
            monitor.record('gc_complete')
            
            final_metrics = monitor.stop()
            
            results[f'size_{size}'] = {
                'data_size': size,
                'total_time': final_metrics['total_time'],
                'peak_memory': final_metrics['peak_memory'],
                'avg_cpu': final_metrics['avg_cpu'],
                'total_clusters': cluster_result['cluster_info']['total_clusters'],
                'noise_points': cluster_result['cluster_info']['noise_points'],
                'memory_per_entry': final_metrics['peak_memory'] / size,
                'time_per_entry': final_metrics['total_time'] / size,
                'clustering_efficiency': cluster_result['cluster_info']['total_clusters'] / final_metrics['total_time'],
                'detailed_metrics': final_metrics['metrics']
            }
        
        self.reporter.generate_report(results, "Clustering Memory Efficiency")
    
    def test_clustering_text_processing_performance(self):
        """Test performance of text processing components in clustering."""
        test_data = self.generator.generate_json_data(1000)
        
        # Test different text processing scenarios
        scenarios = [
            ("short_titles", self._create_short_titles),
            ("long_titles", self._create_long_titles),
            ("diverse_titles", self._create_diverse_titles),
            ("similar_titles", self._create_similar_titles),
            ("multilingual_titles", self._create_multilingual_titles)
        ]
        
        results = {}
        
        for scenario_name, title_generator in scenarios:
            # Generate test data with specific title characteristics
            entries = []
            for i in range(1000):
                entries.append({
                    'title': title_generator(i),
                    'url': f'https://youtube.com/watch?v={i}',
                    'timestamp': '2023-01-01T00:00:00Z'
                })
            
            monitor = PerformanceMonitor()
            times = []
            memories = []
            cluster_counts = []
            
            for _ in range(3):
                monitor.start()
                
                engine = ClusterEngine(eps=0.3, min_samples=5)
                result = engine.cluster_videos(entries)
                
                metrics = monitor.stop()
                times.append(metrics['total_time'])
                memories.append(metrics['peak_memory'])
                cluster_counts.append(result['cluster_info']['total_clusters'])
            
            results[scenario_name] = {
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'avg_memory': np.mean(memories),
                'peak_memory': np.max(memories),
                'avg_clusters': np.mean(cluster_counts),
                'std_clusters': np.std(cluster_counts)
            }
        
        self.reporter.generate_report(results, "Clustering Text Processing Performance")
    
    def test_clustering_concurrent_performance(self):
        """Test clustering performance with concurrent processing."""
        import concurrent.futures
        
        num_datasets = 5
        entries_per_dataset = 500
        
        # Create test datasets
        datasets = []
        for i in range(num_datasets):
            data = self.generator.generate_json_data(entries_per_dataset)
            datasets.append(data['entries'])
        
        # Sequential clustering
        monitor = PerformanceMonitor()
        monitor.start()
        
        sequential_results = []
        for entries in datasets:
            engine = ClusterEngine(eps=0.3, min_samples=5)
            result = engine.cluster_videos(entries)
            sequential_results.append(result)
        
        sequential_metrics = monitor.stop()
        
        # Concurrent clustering
        def cluster_dataset(entries):
            engine = ClusterEngine(eps=0.3, min_samples=5)
            return engine.cluster_videos(entries)
        
        monitor = PerformanceMonitor()
        monitor.start()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            concurrent_results = list(executor.map(cluster_dataset, datasets))
        
        concurrent_metrics = monitor.stop()
        
        results = {
            'sequential_clustering': {
                'total_time': sequential_metrics['total_time'],
                'peak_memory': sequential_metrics['peak_memory'],
                'avg_cpu': sequential_metrics['avg_cpu'],
                'datasets_processed': len(datasets),
                'total_entries': sum(len(d) for d in datasets),
                'total_clusters': sum(r['cluster_info']['total_clusters'] for r in sequential_results)
            },
            'concurrent_clustering': {
                'total_time': concurrent_metrics['total_time'],
                'peak_memory': concurrent_metrics['peak_memory'],
                'avg_cpu': concurrent_metrics['avg_cpu'],
                'datasets_processed': len(datasets),
                'total_entries': sum(len(d) for d in datasets),
                'total_clusters': sum(r['cluster_info']['total_clusters'] for r in concurrent_results),
                'speedup': sequential_metrics['total_time'] / concurrent_metrics['total_time']
            }
        }
        
        self.reporter.generate_report(results, "Clustering Concurrent Performance")
    
    def _analyze_clustering_scalability(self, results):
        """Analyze clustering scalability results."""
        sizes = []
        times = []
        memories = []
        
        for key, result in results.items():
            if key.startswith('size_'):
                size = result['data_size']
                sizes.append(size)
                times.append(result['avg_time'])
                memories.append(result['avg_memory'])
        
        if len(sizes) > 1:
            # Estimate time complexity
            time_poly = np.polyfit(np.log(sizes), np.log(times), 1)
            memory_poly = np.polyfit(np.log(sizes), np.log(memories), 1)
            
            print(f"\nClustering Scalability Analysis:")
            print(f"Time complexity: O(n^{time_poly[0]:.2f})")
            print(f"Memory complexity: O(n^{memory_poly[0]:.2f})")
            
            # Calculate efficiency metrics
            time_per_entry = [t/s for t, s in zip(times, sizes)]
            memory_per_entry = [m/s for m, s in zip(memories, sizes)]
            
            print(f"Average time per entry: {np.mean(time_per_entry):.6f}s")
            print(f"Average memory per entry: {np.mean(memory_per_entry):.2f}MB")
    
    def _cluster_dbscan(self, entries, eps, min_samples):
        """Helper method for DBSCAN clustering."""
        engine = ClusterEngine(eps=eps, min_samples=min_samples)
        return engine.cluster_videos(entries)
    
    def _create_short_titles(self, index):
        """Create short video titles."""
        words = ['AI', 'ML', 'Python', 'Data', 'Code', 'Tech', 'Web', 'App']
        return f"{words[index % len(words)]} {index}"
    
    def _create_long_titles(self, index):
        """Create long video titles."""
        base = "Complete comprehensive tutorial guide for beginners advanced users"
        return f"{base} part {index} detailed explanation with examples"
    
    def _create_diverse_titles(self, index):
        """Create diverse video titles."""
        topics = [
            "Python Programming Tutorial",
            "Machine Learning Fundamentals",
            "Web Development with React",
            "Data Science Analytics",
            "Cloud Computing AWS",
            "Mobile App Development",
            "Cybersecurity Basics",
            "DevOps Pipeline Setup"
        ]
        return f"{topics[index % len(topics)]} - Episode {index}"
    
    def _create_similar_titles(self, index):
        """Create similar video titles for testing clustering."""
        base_titles = [
            "Python Tutorial",
            "Python Guide",
            "Python Lesson",
            "Learn Python",
            "Python Course"
        ]
        return f"{base_titles[index % len(base_titles)]} {index}"
    
    def _create_multilingual_titles(self, index):
        """Create multilingual video titles."""
        titles = [
            "English Tutorial Python Programming",
            "Español Tutorial Programación Python",
            "Français Tutoriel Programmation Python",
            "Deutsch Tutorial Python Programmierung",
            "中文 Python 编程教程"
        ]
        return f"{titles[index % len(titles)]} {index}"


@pytest.mark.benchmark
def test_clustering_benchmark_suite():
    """Run comprehensive clustering benchmark suite."""
    test_instance = TestClusteringPerformance()
    test_instance.setup_method()
    
    try:
        # Run all benchmark tests
        test_instance.test_clustering_scalability()
        test_instance.test_clustering_parameter_optimization()
        test_instance.test_clustering_algorithms_comparison()
        test_instance.test_clustering_memory_efficiency()
        test_instance.test_clustering_text_processing_performance()
        test_instance.test_clustering_concurrent_performance()
        
        print("Clustering benchmark suite completed successfully!")
        
    finally:
        pass


if __name__ == "__main__":
    test_clustering_benchmark_suite()
