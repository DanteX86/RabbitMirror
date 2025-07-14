API Reference
=============

This section contains the complete API reference for RabbitMirror.

Core Modules
------------

.. toctree::
   :maxdepth: 2

   parser
   clustering
   export
   analysis
   visualization
   exceptions
   error_recovery

Overview
--------

RabbitMirror provides a comprehensive set of APIs for analyzing YouTube watch history data. The main components are:

**Core Processing**
   - :doc:`parser` - Parse YouTube watch history HTML files
   - :doc:`clustering` - Cluster videos based on content similarity
   - :doc:`export` - Export data to various formats

**Analysis & Visualization**
   - :doc:`analysis` - Advanced analytics and pattern detection
   - :doc:`visualization` - Generate charts and visualizations

**Infrastructure**
   - :doc:`exceptions` - Custom exception hierarchy
   - :doc:`error_recovery` - Error handling and recovery mechanisms

Quick API Overview
------------------

Core Classes
^^^^^^^^^^^^

.. currentmodule:: rabbitmirror

.. autosummary::
   :toctree: _autosummary

   HistoryParser
   ClusterEngine
   ExportFormatter
   TrendAnalyzer
   AdversarialProfiler
   DashboardGenerator
   ReportGenerator

Exception Classes
^^^^^^^^^^^^^^^^^

.. currentmodule:: rabbitmirror.exceptions

.. autosummary::
   :toctree: _autosummary

   RabbitMirrorError
   ParsingError
   ClusteringError
   ExportError
   ValidationError
   NetworkError
   TimeoutError

Error Recovery
^^^^^^^^^^^^^^

.. currentmodule:: rabbitmirror.error_recovery

.. autosummary::
   :toctree: _autosummary

   ErrorRecoveryManager
   CircuitBreaker
   RetryConfig
   with_retry
   with_timeout
   robust_operation

Common Usage Patterns
^^^^^^^^^^^^^^^^^^^^^

Basic Analysis Pipeline
"""""""""""""""""""""""

.. code-block:: python

   from rabbitmirror import HistoryParser, ClusterEngine, ExportFormatter

   # Parse data
   parser = HistoryParser("watch-history.html")
   data = parser.parse()

   # Analyze patterns
   engine = ClusterEngine(eps=0.3, min_samples=5)
   clusters = engine.cluster_videos(data["entries"])

   # Export results
   formatter = ExportFormatter("output/")
   formatter.export_data(clusters, "json", "results")

Advanced Analysis
"""""""""""""""""

.. code-block:: python

   from rabbitmirror import TrendAnalyzer, AdversarialProfiler

   # Trend analysis
   trend_analyzer = TrendAnalyzer()
   trends = trend_analyzer.analyze_trends(data["entries"])

   # Behavioral profiling
   profiler = AdversarialProfiler()
   profile = profiler.generate_profile(data["entries"])

Error Handling
""""""""""""""

.. code-block:: python

   from rabbitmirror.exceptions import ParsingError, ClusteringError
   from rabbitmirror.error_recovery import with_retry, CircuitBreaker

   @with_retry(max_attempts=3, backoff_factor=2)
   def robust_analysis(data):
       try:
           return perform_analysis(data)
       except ParsingError as e:
           logger.error(f"Parsing failed: {e}")
           raise
       except ClusteringError as e:
           logger.error(f"Clustering failed: {e}")
           return fallback_analysis(data)

Configuration
^^^^^^^^^^^^^

.. code-block:: python

   from rabbitmirror.config import ConfigManager

   # Load configuration
   config = ConfigManager("config.yaml")

   # Use configuration
   parser = HistoryParser(
       file_path="history.html",
       encoding=config.get("parser.encoding", "utf-8"),
       timeout=config.get("parser.timeout", 30)
   )

Type Hints
^^^^^^^^^^

RabbitMirror uses comprehensive type hints throughout the codebase:

.. code-block:: python

   from typing import List, Dict, Any, Optional
   from rabbitmirror.types import VideoEntry, ClusterResult, AnalysisResult

   def analyze_videos(
       entries: List[VideoEntry],
       config: Optional[Dict[str, Any]] = None
   ) -> AnalysisResult:
       # Implementation
       pass

See Also
--------

- :doc:`../getting_started` - Getting started guide
- :doc:`../tutorials/index` - Comprehensive tutorials
- :doc:`../examples/index` - Example usage patterns
- :doc:`../configuration` - Configuration options
