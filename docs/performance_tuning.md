# RabbitMirror Performance Tuning Guide

## Overview

This guide provides comprehensive strategies for optimizing RabbitMirror's performance across different system configurations and dataset sizes. Whether you're processing small personal watch histories or large-scale research datasets, these tuning techniques will help you maximize efficiency and minimize processing time.

## Performance Fundamentals

### Key Performance Metrics

RabbitMirror performance is measured across several dimensions:

- **Parse Time**: Time to extract data from HTML files
- **Analysis Time**: Time for clustering, pattern detection, and trend analysis
- **Memory Usage**: RAM consumption during processing
- **Disk I/O**: Read/write operations for data and results
- **CPU Utilization**: Processor usage across cores

### Performance Bottlenecks

Common performance bottlenecks include:

1. **Memory constraints** with large datasets
2. **Single-threaded operations** on multi-core systems
3. **Inefficient clustering parameters** causing excessive computation
4. **Disk I/O delays** with slow storage
5. **Network delays** when using web interface features

## System Requirements and Sizing

### Minimum System Requirements

```bash
# Small datasets (<1,000 videos)
CPU: 2 cores, 2.0 GHz
RAM: 2 GB
Storage: 1 GB free space
Python: 3.8+
```

### Recommended System Requirements

```bash
# Medium datasets (1,000-10,000 videos)
CPU: 4 cores, 2.5 GHz
RAM: 8 GB
Storage: 5 GB free space (SSD preferred)
Python: 3.9+
```

### High-Performance System Requirements

```bash
# Large datasets (>10,000 videos)
CPU: 8+ cores, 3.0 GHz
RAM: 16+ GB
Storage: 20+ GB free space (NVMe SSD)
Python: 3.10+
```

## Dataset Size Optimization

### Small Datasets (<1,000 videos)

**Optimal Configuration:**
```bash
# Basic performance settings
rabbitmirror config set max_workers 2
rabbitmirror config set clustering_max_features 500
rabbitmirror config set cache_enabled false
rabbitmirror config set parallel_processing false

# Clustering optimization
rabbitmirror config set clustering_eps 0.4
rabbitmirror config set clustering_min_samples 3
```

**Processing Approach:**
```bash
# Single-step processing
rabbitmirror process parse history.html --output data.json
rabbitmirror analyze cluster data.json --output results.json
rabbitmirror report generate-report data.json --output-dir reports/
```

### Medium Datasets (1,000-10,000 videos)

**Optimal Configuration:**
```bash
# Balanced performance settings
rabbitmirror config set max_workers 4
rabbitmirror config set clustering_max_features 1000
rabbitmirror config set cache_enabled true
rabbitmirror config set cache_size "200MB"
rabbitmirror config set parallel_processing true

# Memory management
rabbitmirror config set max_memory_usage "4GB"
```

**Processing Approach:**
```bash
# Chunked processing with progress tracking
rabbitmirror process parse history.html --chunk-size 1000 --output data.json
rabbitmirror analyze cluster data.json --batch-size 500 --output clusters.json
```

### Large Datasets (>10,000 videos)

**Optimal Configuration:**
```bash
# High-performance settings
rabbitmirror config set max_workers 8
rabbitmirror config set clustering_max_features 2000
rabbitmirror config set cache_enabled true
rabbitmirror config set cache_size "1GB"
rabbitmirror config set parallel_processing true
rabbitmirror config set max_memory_usage "12GB"

# Advanced clustering optimization
rabbitmirror config set clustering_algorithm "MiniBatchKMeans"
rabbitmirror config set clustering_batch_size 1000
```

**Processing Approach:**
```bash
# Multi-stage processing pipeline
rabbitmirror process parse history.html --streaming --output data.json
rabbitmirror analyze cluster data.json --parallel --output clusters.json
rabbitmirror analyze detect-patterns data.json --async --output patterns.json
```

## CPU Optimization

### Multi-Core Utilization

**Determine Optimal Worker Count:**
```bash
# Check available CPU cores
python -c "import os; print(f'CPU cores: {os.cpu_count()}')"

# Set workers based on CPU cores (recommended: cores - 1)
rabbitmirror config set max_workers $(($(nproc) - 1))
```

**CPU-Intensive Operations:**
```bash
# Clustering optimization
rabbitmirror config set clustering_n_jobs -1  # Use all available cores
rabbitmirror config set feature_extraction_parallel true

# Pattern detection optimization
rabbitmirror config set pattern_detection_parallel true
rabbitmirror config set pattern_detection_batch_size 100
```

### CPU Architecture Considerations

**Intel/AMD x86-64:**
```bash
# Optimize for SIMD instructions
rabbitmirror config set use_optimized_libraries true
rabbitmirror config set numpy_threads 4
```

**Apple Silicon (M1/M2):**
```bash
# Optimize for ARM64 architecture
rabbitmirror config set use_accelerated_blas true
rabbitmirror config set metal_performance_shaders true
```

## Memory Optimization

### Memory Usage Patterns

**Monitor Memory Usage:**
```bash
# Check current memory usage
ps aux | grep rabbitmirror
top -p $(pgrep rabbitmirror)

# Enable memory profiling
rabbitmirror config set enable_memory_profiling true
rabbitmirror config set memory_profile_output "logs/memory_profile.log"
```

### Memory-Constrained Systems

**Low Memory Configuration (<4GB RAM):**
```bash
# Aggressive memory optimization
rabbitmirror config set max_memory_usage "1GB"
rabbitmirror config set streaming_parser true
rabbitmirror config set clustering_max_features 200
rabbitmirror config set cache_enabled false
rabbitmirror config set batch_processing_size 100

# Use memory-efficient algorithms
rabbitmirror config set clustering_algorithm "MiniBatchKMeans"
rabbitmirror config set use_sparse_matrices true
```

**Processing Strategy:**
```bash
# Process in small chunks
rabbitmirror process parse history.html --chunk-size 100 --streaming
rabbitmirror analyze cluster data.json --memory-limit 500MB --batch-size 50
```

### High-Memory Systems

**High Memory Configuration (>16GB RAM):**
```bash
# Utilize available memory
rabbitmirror config set max_memory_usage "12GB"
rabbitmirror config set cache_size "2GB"
rabbitmirror config set preload_data true
rabbitmirror config set clustering_max_features 5000

# Enable memory-intensive optimizations
rabbitmirror config set use_memory_mapping true
rabbitmirror config set aggressive_caching true
```

## Storage and I/O Optimization

### Storage Type Optimization

**SSD Storage:**
```bash
# Optimize for SSD
rabbitmirror config set io_buffer_size "64KB"
rabbitmirror config set concurrent_io_operations 4
rabbitmirror config set use_async_io true
```

**HDD Storage:**
```bash
# Optimize for traditional hard drives
rabbitmirror config set io_buffer_size "1MB"
rabbitmirror config set concurrent_io_operations 1
rabbitmirror config set sequential_io_preferred true
```

### Temporary File Management

```bash
# Configure temporary storage
export RABBITMIRROR_TEMP_DIR="/path/to/fast/storage"
rabbitmirror config set temp_file_cleanup true
rabbitmirror config set temp_file_threshold "100MB"
```

### Output Optimization

```bash
# Compression for large outputs
rabbitmirror config set export_compression true
rabbitmirror config set compression_level 6
rabbitmirror config set compression_format "gzip"

# Batch writing
rabbitmirror config set batch_write_size 1000
rabbitmirror config set write_buffer_size "10MB"
```

## Algorithm-Specific Optimization

### Clustering Performance

**DBSCAN Optimization:**
```bash
# Optimize DBSCAN parameters for performance
rabbitmirror config set clustering_algorithm "DBSCAN"
rabbitmirror config set clustering_eps 0.3
rabbitmirror config set clustering_min_samples 5
rabbitmirror config set clustering_metric "cosine"
rabbitmirror config set clustering_algorithm_backend "sklearn"
```

**K-Means Optimization:**
```bash
# Optimize K-Means for large datasets
rabbitmirror config set clustering_algorithm "MiniBatchKMeans"
rabbitmirror config set clustering_n_clusters 10
rabbitmirror config set clustering_batch_size 1000
rabbitmirror config set clustering_max_iter 300
rabbitmirror config set clustering_tol 1e-4
```

**Hierarchical Clustering:**
```bash
# Optimize for hierarchical clustering
rabbitmirror config set clustering_algorithm "AgglomerativeClustering"
rabbitmirror config set clustering_linkage "ward"
rabbitmirror config set clustering_connectivity "kneighbors"
rabbitmirror config set clustering_memory_limit "2GB"
```

### Text Processing Optimization

```bash
# Feature extraction optimization
rabbitmirror config set text_vectorizer "TfidfVectorizer"
rabbitmirror config set max_features 2000
rabbitmirror config set ngram_range "[1, 2]"
rabbitmirror config set min_df 2
rabbitmirror config set max_df 0.95

# Text preprocessing
rabbitmirror config set remove_stopwords true
rabbitmirror config set use_stemming false  # Faster than stemming
rabbitmirror config set use_lemmatization false  # Use only if accuracy is critical
```

## Benchmarking and Profiling

### Performance Benchmarking

**Built-in Benchmarking:**
```bash
# Run performance benchmark
rabbitmirror utils benchmark --dataset-size 1000 --output benchmark_results.json

# Compare configurations
rabbitmirror utils benchmark --config config1.yaml --config config2.yaml --compare
```

**Custom Benchmarking Script:**
```python
#!/usr/bin/env python3
import time
import psutil
import subprocess
from pathlib import Path

def benchmark_rabbitmirror(input_file, config_file=None):
    """Benchmark RabbitMirror performance."""
    start_time = time.time()
    start_memory = psutil.virtual_memory().used

    cmd = ["rabbitmirror", "analyze", "cluster", input_file]
    if config_file:
        cmd.extend(["--config", config_file])

    result = subprocess.run(cmd, capture_output=True, text=True)

    end_time = time.time()
    end_memory = psutil.virtual_memory().used

    return {
        "processing_time": end_time - start_time,
        "memory_used": end_memory - start_memory,
        "success": result.returncode == 0
    }
```

### Profiling Tools

**Python Profiling:**
```bash
# CPU profiling
python -m cProfile -o profile.stats -m rabbitmirror analyze cluster history.html

# Memory profiling
pip install memory-profiler
python -m memory_profiler -m rabbitmirror analyze cluster history.html
```

**System Monitoring:**
```bash
# Monitor system resources during processing
htop &
iotop &
rabbitmirror analyze cluster history.html
```

## Network and Distributed Processing

### Web Interface Optimization

```bash
# Web interface performance
rabbitmirror config set web_interface_threads 4
rabbitmirror config set web_interface_timeout 300
rabbitmirror config set web_interface_cache true
rabbitmirror config set web_interface_compression true
```

### Database Integration Performance

```bash
# Database optimization
rabbitmirror config set database_connection_pool_size 10
rabbitmirror config set database_query_timeout 30
rabbitmirror config set database_batch_insert_size 1000
```

## Environment-Specific Optimizations

### Docker Container Optimization

**Dockerfile optimization:**
```dockerfile
# Multi-stage build for smaller image
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Optimize container resources
ENV PYTHONUNBUFFERED=1
ENV RABBITMIRROR_MAX_WORKERS=4
ENV RABBITMIRROR_MAX_MEMORY_USAGE="2GB"
```

**Container runtime optimization:**
```bash
# Run with optimized settings
docker run -d \
  --memory=4g \
  --cpus=4 \
  --env RABBITMIRROR_PARALLEL_PROCESSING=true \
  rabbitmirror:latest
```

### Cloud Platform Optimization

**AWS EC2:**
```bash
# Instance type recommendations
# c5.large: CPU-intensive workloads
# r5.large: Memory-intensive workloads
# m5.large: Balanced workloads

# EBS volume optimization
rabbitmirror config set storage_type "gp3"
rabbitmirror config set iops 3000
```

**Google Cloud Platform:**
```bash
# Machine type recommendations
# c2-standard-4: CPU-intensive
# n1-highmem-4: Memory-intensive
# n1-standard-4: Balanced

# Persistent disk optimization
rabbitmirror config set disk_type "pd-ssd"
```

## Performance Monitoring

### Real-time Monitoring

**Enable Performance Logging:**
```bash
# Configure performance monitoring
rabbitmirror config set performance_monitoring true
rabbitmirror config set performance_log_file "logs/performance.log"
rabbitmirror config set performance_metrics_interval 5
```

**Monitor Key Metrics:**
```python
# Custom monitoring script
import json
import time
from rabbitmirror.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start()

# Your processing code here
# ...

metrics = monitor.stop()
print(json.dumps(metrics, indent=2))
```

### Performance Alerts

```bash
# Set performance thresholds
rabbitmirror config set performance_alert_memory_threshold "80%"
rabbitmirror config set performance_alert_processing_time_threshold 300
rabbitmirror config set performance_alert_email "admin@example.com"
```

## Troubleshooting Performance Issues

### Common Performance Problems

#### 1. Slow Parsing

**Diagnosis:**
```bash
# Check file size and encoding
ls -lh history.html
file history.html
```

**Solutions:**
```bash
# Optimize parser settings
rabbitmirror config set parser_timeout 120
rabbitmirror config set parser_encoding "utf-8"
rabbitmirror config set parser_fallback_encodings '["utf-8-sig"]'
```

#### 2. Memory Issues

**Diagnosis:**
```bash
# Monitor memory usage
free -h
rabbitmirror config get max_memory_usage
```

**Solutions:**
```bash
# Reduce memory usage
rabbitmirror config set streaming_parser true
rabbitmirror config set clustering_max_features 500
rabbitmirror config set batch_processing_size 100
```

#### 3. Slow Clustering

**Diagnosis:**
```bash
# Check clustering parameters
rabbitmirror config get clustering_eps
rabbitmirror config get clustering_min_samples
rabbitmirror config get clustering_max_features
```

**Solutions:**
```bash
# Optimize clustering
rabbitmirror config set clustering_eps 0.5  # Increase for faster clustering
rabbitmirror config set clustering_algorithm "MiniBatchKMeans"
rabbitmirror config set clustering_max_features 1000
```

### Performance Debugging

**Enable Debug Profiling:**
```bash
# Detailed performance profiling
rabbitmirror config set debug_profiling true
rabbitmirror config set profile_output_dir "profiles/"
rabbitmirror analyze cluster history.html --profile
```

**Analyze Profile Results:**
```python
import pstats
from pstats import SortKey

# Analyze CPU profile
p = pstats.Stats('profiles/cluster_profile.stats')
p.sort_stats(SortKey.CUMULATIVE)
p.print_stats(20)
```

## Performance Best Practices

### General Guidelines

1. **Start with defaults** and benchmark before optimizing
2. **Profile first** to identify actual bottlenecks
3. **Optimize incrementally** and measure impact
4. **Consider trade-offs** between speed and accuracy
5. **Monitor resource usage** during processing

### Configuration Templates

**High-Performance Template:**
```json
{
  "max_workers": 8,
  "max_memory_usage": "8GB",
  "parallel_processing": true,
  "clustering_algorithm": "MiniBatchKMeans",
  "clustering_max_features": 2000,
  "cache_enabled": true,
  "cache_size": "1GB",
  "use_optimized_libraries": true,
  "streaming_parser": false,
  "batch_processing_size": 1000
}
```

**Memory-Efficient Template:**
```json
{
  "max_workers": 2,
  "max_memory_usage": "1GB",
  "streaming_parser": true,
  "clustering_max_features": 200,
  "cache_enabled": false,
  "batch_processing_size": 50,
  "use_sparse_matrices": true,
  "clustering_algorithm": "MiniBatchKMeans"
}
```

**Balanced Template:**
```json
{
  "max_workers": 4,
  "max_memory_usage": "4GB",
  "parallel_processing": true,
  "clustering_max_features": 1000,
  "cache_enabled": true,
  "cache_size": "200MB",
  "batch_processing_size": 500,
  "clustering_eps": 0.3,
  "clustering_min_samples": 5
}
```

## Performance Testing Framework

### Automated Performance Tests

```python
#!/usr/bin/env python3
"""Performance testing framework for RabbitMirror."""

import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List

class PerformanceTest:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.results = []

    def run_test(self, config: Dict, input_file: str) -> Dict:
        """Run a single performance test."""
        # Set configuration
        for key, value in config.items():
            subprocess.run([
                "rabbitmirror", "config", "set", key, str(value)
            ])

        # Run analysis with timing
        start_time = time.time()
        result = subprocess.run([
            "rabbitmirror", "analyze", "cluster", input_file
        ], capture_output=True)
        end_time = time.time()

        return {
            "config": config,
            "processing_time": end_time - start_time,
            "success": result.returncode == 0,
            "memory_peak": self.get_peak_memory(),
            "timestamp": time.time()
        }

    def run_benchmark_suite(self, configs: List[Dict], input_file: str):
        """Run complete benchmark suite."""
        for i, config in enumerate(configs):
            print(f"Running test {i+1}/{len(configs)}: {config}")
            result = self.run_test(config, input_file)
            self.results.append(result)
            time.sleep(5)  # Cool-down between tests

    def generate_report(self) -> str:
        """Generate performance report."""
        report = {
            "test_name": self.test_name,
            "timestamp": time.time(),
            "results": self.results,
            "summary": {
                "best_config": min(self.results, key=lambda x: x["processing_time"]),
                "worst_config": max(self.results, key=lambda x: x["processing_time"]),
                "average_time": sum(r["processing_time"] for r in self.results) / len(self.results)
            }
        }
        return json.dumps(report, indent=2)

# Usage example
if __name__ == "__main__":
    test_configs = [
        {"max_workers": 2, "clustering_eps": 0.3},
        {"max_workers": 4, "clustering_eps": 0.3},
        {"max_workers": 8, "clustering_eps": 0.3},
    ]

    perf_test = PerformanceTest("worker_scaling_test")
    perf_test.run_benchmark_suite(test_configs, "sample_history.html")
    print(perf_test.generate_report())
```

## See Also

- [Configuration Guide](configuration.md)
- [API Reference](api_reference.md)
- [Advanced Usage](tutorials/02_advanced_usage.md)
- [Troubleshooting FAQ](FAQ.md)
