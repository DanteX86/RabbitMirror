Parser Module
=============

.. currentmodule:: rabbitmirror.parser

The parser module provides functionality for parsing YouTube watch history HTML files into structured data.

Classes
-------

HistoryParser
^^^^^^^^^^^^^

.. autoclass:: HistoryParser
   :members:
   :undoc-members:
   :show-inheritance:

   The main class for parsing YouTube watch history files.

   .. rubric:: Example Usage

   .. code-block:: python

      from rabbitmirror.parser import HistoryParser

      # Basic usage
      parser = HistoryParser("watch-history.html")
      data = parser.parse()

      # With custom configuration
      parser = HistoryParser(
          file_path="history.html",
          encoding="utf-8",
          timeout=30
      )
      data = parser.parse()

   .. rubric:: Attributes

   .. autoattribute:: file_path
      :annotation: = str

      Path to the HTML file to parse.

   .. autoattribute:: retry_config
      :annotation: = RetryConfig

      Configuration for retry behavior.

   .. rubric:: Methods

   .. automethod:: parse
   .. automethod:: _parse_with_fallback
   .. automethod:: _extract_entries
   .. automethod:: _parse_entry
   .. automethod:: _convert_timestamp

Functions
---------

.. autofunction:: parse_youtube_history

   Convenience function for parsing YouTube watch history files.

   :param file_path: Path to the HTML file
   :type file_path: str
   :param encoding: File encoding (default: "utf-8")
   :type encoding: str
   :param timeout: Parse timeout in seconds (default: 30)
   :type timeout: int
   :return: Parsed data dictionary
   :rtype: dict

   .. rubric:: Example

   .. code-block:: python

      from rabbitmirror.parser import parse_youtube_history

      data = parse_youtube_history("watch-history.html")

Data Structures
---------------

The parser module works with the following data structures:

Parsed Data Format
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   {
       "metadata": {
           "source": "YouTube Watch History",
           "parsed_at": "2023-12-15T14:30:45Z",
           "total_entries": 1000,
           "date_range": {
               "start": "2023-01-01T00:00:00Z",
               "end": "2023-12-15T14:30:45Z"
           }
       },
       "entries": [
           {
               "title": "Video Title",
               "url": "https://www.youtube.com/watch?v=...",
               "timestamp": "2023-12-15T14:30:45Z"
           },
           # ... more entries
       ]
   }

Entry Format
^^^^^^^^^^^^

Each video entry contains:

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - title
     - str
     - Video title
   * - url
     - str
     - YouTube video URL
   * - timestamp
     - str
     - ISO 8601 formatted timestamp

Error Handling
--------------

The parser module includes comprehensive error handling:

.. autoexception:: rabbitmirror.exceptions.ParsingError
   :show-inheritance:

Common parsing errors and solutions:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Error
     - Solution
   * - ``FileNotFoundError``
     - Check file path exists
   * - ``UnicodeDecodeError``
     - Try different encoding or enable fallback
   * - ``InvalidFormatError``
     - Verify HTML file format
   * - ``ParsingError``
     - Check file content and structure

Configuration
-------------

Parser behavior can be configured through:

.. code-block:: python

   from rabbitmirror.parser import HistoryParser
   from rabbitmirror.error_recovery import RetryConfig

   parser = HistoryParser(
       file_path="history.html",
       retry_config=RetryConfig(
           max_attempts=3,
           base_delay=0.5,
           retryable_exceptions=[OSError, IOError]
       )
   )

Advanced Usage
--------------

Custom Parsing
^^^^^^^^^^^^^^

For custom parsing logic, you can extend the HistoryParser class:

.. code-block:: python

   from rabbitmirror.parser import HistoryParser
   from typing import Dict, Any, List

   class CustomParser(HistoryParser):
       def _parse_entry(self, entry) -> Dict[str, Any]:
           # Custom parsing logic
           result = super()._parse_entry(entry)
           
           # Add custom fields
           result["custom_field"] = self._extract_custom_field(entry)
           
           return result
       
       def _extract_custom_field(self, entry) -> str:
           # Custom extraction logic
           return "custom_value"

Batch Processing
^^^^^^^^^^^^^^^^

Process multiple files:

.. code-block:: python

   from pathlib import Path
   from rabbitmirror.parser import HistoryParser

   def parse_multiple_files(file_paths: List[str]) -> List[Dict[str, Any]]:
       results = []
       for file_path in file_paths:
           parser = HistoryParser(file_path)
           data = parser.parse()
           results.append(data)
       return results

   # Usage
   html_files = list(Path("data/").glob("*.html"))
   all_data = parse_multiple_files([str(f) for f in html_files])

Performance Considerations
--------------------------

For large files, consider:

1. **Memory Management**: Use streaming for very large files
2. **Encoding Detection**: Specify encoding explicitly if known
3. **Error Recovery**: Enable retry mechanisms for unreliable environments
4. **Parallel Processing**: Process multiple files in parallel

.. code-block:: python

   from concurrent.futures import ThreadPoolExecutor
   from rabbitmirror.parser import HistoryParser

   def parse_file(file_path: str) -> Dict[str, Any]:
       parser = HistoryParser(file_path)
       return parser.parse()

   # Parallel processing
   with ThreadPoolExecutor(max_workers=4) as executor:
       results = list(executor.map(parse_file, file_paths))

See Also
--------

- :doc:`clustering` - Cluster parsed data
- :doc:`export` - Export parsed data
- :doc:`exceptions` - Exception handling
- :doc:`error_recovery` - Error recovery mechanisms
