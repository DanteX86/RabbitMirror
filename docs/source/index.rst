RabbitMirror Documentation
=========================

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/release/python-380/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/yourusername/RabbitMirror/blob/main/LICENSE
   :alt: MIT License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

**RabbitMirror** is a comprehensive Python toolkit for analyzing YouTube watch history data. It provides powerful parsing, clustering, analysis, and visualization capabilities to help you understand your digital viewing patterns and behaviors.

Features
--------

🔍 **Intelligent Parsing**
   - Robust HTML parsing with encoding detection
   - Error recovery and fallback mechanisms
   - Support for various YouTube data formats

📊 **Advanced Analytics**
   - Clustering analysis with DBSCAN and other algorithms
   - Temporal pattern analysis
   - Behavioral profiling and trend detection

📈 **Rich Visualizations**
   - Interactive dashboards
   - Timeline visualizations
   - Clustering and network graphs

🔧 **Flexible Export**
   - Multiple export formats (JSON, CSV, Excel, YAML, HTML)
   - Custom templates and styling
   - Batch processing capabilities

🛡️ **Enterprise-Ready**
   - Comprehensive error handling
   - Circuit breaker patterns
   - Retry mechanisms and timeouts

🔌 **Extensible Architecture**
   - Plugin system for custom analyzers
   - Modular design for easy extension
   - Well-documented APIs

Quick Start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install rabbitmirror

Basic Usage
^^^^^^^^^^^

.. code-block:: python

   from rabbitmirror import HistoryParser, ClusterEngine, ExportFormatter

   # Parse YouTube watch history
   parser = HistoryParser("watch-history.html")
   data = parser.parse()

   # Perform clustering analysis
   cluster_engine = ClusterEngine(eps=0.3, min_samples=5)
   clusters = cluster_engine.cluster_videos(data["entries"])

   # Export results
   formatter = ExportFormatter("output/")
   formatter.export_data(clusters, "json", "analysis_results")

Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Parse watch history
   python -m rabbitmirror.cli parse watch-history.html

   # Perform clustering
   python -m rabbitmirror.cli cluster parsed_data.json --eps 0.3

   # Generate reports
   python -m rabbitmirror.cli report parsed_data.json --output-dir reports/

   # Export to different formats
   python -m rabbitmirror.cli export parsed_data.json --format excel

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   installation
   tutorials/index
   examples/index
   configuration
   cli_reference

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
   api/parser
   api/clustering
   api/export
   api/analysis
   api/visualization
   api/exceptions
   api/error_recovery

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide

   contributing
   development
   testing
   architecture
   plugins

.. toctree::
   :maxdepth: 1
   :caption: About

   changelog
   license
   support

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Community & Support
===================

- **GitHub**: https://github.com/yourusername/RabbitMirror
- **Documentation**: https://rabbitmirror.readthedocs.io/
- **Issues**: https://github.com/yourusername/RabbitMirror/issues
- **Discussions**: https://github.com/yourusername/RabbitMirror/discussions

License
=======

This project is licensed under the MIT License - see the :doc:`license` page for details.

.. note::
   RabbitMirror is designed to help you analyze your own YouTube watch history data.
   Please ensure you comply with YouTube's Terms of Service and applicable privacy laws
   when using this tool.
