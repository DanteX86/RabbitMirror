Error Recovery Module
=====================

The error recovery module provides comprehensive error handling capabilities with retry mechanisms, circuit breakers, fallback strategies, and health monitoring.

.. currentmodule:: rabbitmirror.error_recovery

Core Classes
------------

RetryConfig
~~~~~~~~~~~

.. autoclass:: RetryConfig
   :members:
   :show-inheritance:

Configuration class for retry behavior.

**Parameters:**
- ``max_attempts`` (int): Maximum number of retry attempts (default: 3)
- ``base_delay`` (float): Base delay between retries in seconds (default: 1.0)
- ``max_delay`` (float): Maximum delay between retries in seconds (default: 60.0)
- ``exponential_base`` (float): Exponential backoff base (default: 2.0)
- ``jitter`` (bool): Whether to add jitter to delays (default: True)
- ``retryable_exceptions`` (list): List of exception types that should trigger retries

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import RetryConfig

   # Basic configuration
   config = RetryConfig(max_attempts=5, base_delay=2.0)

   # Advanced configuration
   config = RetryConfig(
       max_attempts=3,
       base_delay=1.0,
       max_delay=30.0,
       exponential_base=2.0,
       jitter=True,
       retryable_exceptions=[NetworkError, FileOperationError]
   )

CircuitBreaker
~~~~~~~~~~~~~~

.. autoclass:: CircuitBreaker
   :members:
   :show-inheritance:

Circuit breaker implementation for error handling.

**Parameters:**
- ``failure_threshold`` (int): Number of failures before opening circuit (default: 5)
- ``recovery_timeout`` (int): Time in seconds before attempting recovery (default: 60)
- ``expected_exception`` (type): Exception type to monitor (default: Exception)

**States:**
- ``CLOSED``: Normal operation, calls pass through
- ``OPEN``: Circuit is open, calls fail immediately
- ``HALF_OPEN``: Testing recovery, single call allowed

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import CircuitBreaker

   # Create circuit breaker
   breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

   # Use circuit breaker
   try:
       result = breaker.call(risky_function, arg1, arg2)
   except Exception as e:
       print(f"Circuit breaker protected call failed: {e}")

ErrorRecoveryManager
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ErrorRecoveryManager
   :members:
   :show-inheritance:

Manages error recovery strategies and circuit breakers.

**Methods:**
- ``register_recovery_strategy(error_type, strategy)``: Register a recovery strategy
- ``get_circuit_breaker(service_name)``: Get or create circuit breaker for service
- ``attempt_recovery(error, context)``: Attempt recovery using registered strategies

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import ErrorRecoveryManager

   # Create recovery manager
   manager = ErrorRecoveryManager()

   # Register recovery strategy
   def network_recovery(error):
       time.sleep(5)  # Wait before retry
       return "recovered"

   manager.register_recovery_strategy(NetworkError, network_recovery)

   # Get circuit breaker
   breaker = manager.get_circuit_breaker("api_service")

ErrorHealthMonitor
~~~~~~~~~~~~~~~~~~

.. autoclass:: ErrorHealthMonitor
   :members:
   :show-inheritance:

Monitors error patterns and system health.

**Parameters:**
- ``window_size`` (int): Maximum number of errors to track (default: 100)

**Methods:**
- ``record_error(error, context)``: Record an error occurrence
- ``get_error_rate(time_window_minutes)``: Calculate error rate within time window
- ``get_most_common_errors(limit)``: Get most frequent error types
- ``is_system_healthy()``: Check if system is healthy based on error patterns
- ``get_health_report()``: Get comprehensive health report

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import ErrorHealthMonitor

   # Create monitor
   monitor = ErrorHealthMonitor(window_size=50)

   # Record errors
   monitor.record_error(ValueError("Test error"), {"context": "test"})

   # Get health information
   error_rate = monitor.get_error_rate(time_window_minutes=5)
   is_healthy = monitor.is_system_healthy()
   health_report = monitor.get_health_report()

Decorators
----------

with_retry
~~~~~~~~~~

.. autofunction:: with_retry

Decorator that adds retry functionality to functions.

**Parameters:**
- ``config`` (RetryConfig, optional): Retry configuration
- ``recovery_manager`` (ErrorRecoveryManager, optional): Error recovery manager

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import with_retry, RetryConfig

   @with_retry(config=RetryConfig(max_attempts=3, base_delay=1.0))
   def fetch_data():
       # Your data fetching logic
       pass

with_circuit_breaker
~~~~~~~~~~~~~~~~~~~~

.. autofunction:: with_circuit_breaker

Decorator that adds circuit breaker protection to functions.

**Parameters:**
- ``service_name`` (str): Name of the service for circuit breaker identification
- ``circuit_breaker_config`` (dict, optional): Circuit breaker configuration

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import with_circuit_breaker

   @with_circuit_breaker("external_api", {"failure_threshold": 3})
   def call_external_api():
       # Your API call logic
       pass

with_timeout
~~~~~~~~~~~~

.. autofunction:: with_timeout

Decorator that adds timeout protection to functions.

**Parameters:**
- ``timeout_seconds`` (float): Timeout duration in seconds

.. note::
   Timeout functionality may not work on all platforms due to signal handling differences.

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import with_timeout

   @with_timeout(timeout_seconds=5.0)
   def time_sensitive_operation():
       # Your time-sensitive logic
       pass

with_fallback
~~~~~~~~~~~~~

.. autofunction:: with_fallback

Decorator that provides fallback functionality when the main function fails.

**Parameters:**
- ``fallback_func`` (callable): Function to call when main function fails

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import with_fallback

   @with_fallback(lambda: "default_value")
   def risky_operation():
       # Your risky logic
       pass

robust_operation
~~~~~~~~~~~~~~~~

.. autofunction:: robust_operation

Decorator that combines multiple error handling strategies.

**Parameters:**
- ``retry_config`` (RetryConfig, optional): Retry configuration
- ``circuit_breaker_service`` (str, optional): Circuit breaker service name
- ``timeout_seconds`` (float, optional): Timeout duration
- ``fallback_func`` (callable, optional): Fallback function

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import robust_operation, RetryConfig

   @robust_operation(
       retry_config=RetryConfig(max_attempts=3),
       circuit_breaker_service="api_service",
       timeout_seconds=10.0,
       fallback_func=lambda: "fallback_result"
   )
   def complex_operation():
       # Your complex logic
       pass

monitor_errors
~~~~~~~~~~~~~~

.. autofunction:: monitor_errors

Decorator that monitors function errors and records them in the health monitor.

**Example:**

.. code-block:: python

   from rabbitmirror.error_recovery import monitor_errors

   @monitor_errors
   def monitored_function():
       # Your function logic
       pass

Recovery Strategies
-------------------

The module includes pre-configured recovery strategies for common error types:

file_operation_recovery
~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: file_operation_recovery

Recovery strategy for file operation errors.

**Handles:**
- Permission denied errors
- Disk space full errors
- Generic file operation errors

network_operation_recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: network_operation_recovery

Recovery strategy for network operation errors.

**Handles:**
- Rate limiting (429 errors)
- Server errors (5xx errors)
- Client errors (4xx errors)

timeout_operation_recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: timeout_operation_recovery

Recovery strategy for timeout errors.

**Handles:**
- Short timeouts (increases timeout duration)
- Long timeouts (no modification)

Global Instances
----------------

error_recovery_manager
~~~~~~~~~~~~~~~~~~~~~~

.. autodata:: error_recovery_manager

Global instance of :class:`ErrorRecoveryManager` with default recovery strategies registered.

health_monitor
~~~~~~~~~~~~~~

.. autodata:: health_monitor

Global instance of :class:`ErrorHealthMonitor` for system-wide error monitoring.

Usage Examples
--------------

Basic Retry Example
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import with_retry, RetryConfig
   from rabbitmirror.exceptions import NetworkError

   @with_retry(config=RetryConfig(max_attempts=3, base_delay=1.0))
   def fetch_user_data(user_id):
       # Simulate network call that might fail
       response = requests.get(f"https://api.example.com/users/{user_id}")
       if response.status_code != 200:
           raise NetworkError(f"Failed to fetch user data: {response.status_code}")
       return response.json()

Circuit Breaker Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import with_circuit_breaker

   @with_circuit_breaker("payment_service", {"failure_threshold": 2})
   def process_payment(amount, card_token):
       # Payment processing logic that might fail
       response = payment_api.charge(amount, card_token)
       if not response.success:
           raise Exception("Payment failed")
       return response.transaction_id

Combined Error Handling
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import robust_operation, RetryConfig

   @robust_operation(
       retry_config=RetryConfig(max_attempts=3, base_delay=2.0),
       circuit_breaker_service="database",
       timeout_seconds=30.0,
       fallback_func=lambda: {"error": "Database unavailable"}
   )
   def get_user_profile(user_id):
       # Database operation with comprehensive error handling
       return database.get_user_profile(user_id)

Error Monitoring
~~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import monitor_errors, health_monitor

   @monitor_errors
   def critical_operation():
       # Your critical operation
       pass

   # Check system health
   if not health_monitor.is_system_healthy():
       print("System is experiencing issues!")
       report = health_monitor.get_health_report()
       print(f"Error rate: {report['error_rate_per_minute']}")
       print(f"Most common errors: {report['most_common_errors']}")

Best Practices
--------------

1. **Use Appropriate Retry Policies**
   - Only retry transient errors
   - Use exponential backoff with jitter
   - Set reasonable maximum attempts

2. **Circuit Breaker Configuration**
   - Set appropriate failure thresholds
   - Configure recovery timeouts based on service characteristics
   - Monitor circuit breaker states

3. **Fallback Strategies**
   - Provide meaningful fallback values
   - Ensure fallback functions are reliable
   - Consider performance implications

4. **Error Monitoring**
   - Monitor error rates and patterns
   - Set up alerts for unhealthy systems
   - Use health reports for troubleshooting

5. **Testing Error Handling**
   - Test all error scenarios
   - Verify retry behavior
   - Ensure circuit breakers work correctly
   - Test fallback mechanisms

Common Patterns
---------------

Web Service Integration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import robust_operation, RetryConfig

   @robust_operation(
       retry_config=RetryConfig(
           max_attempts=3,
           base_delay=1.0,
           retryable_exceptions=[NetworkError, TimeoutError]
       ),
       circuit_breaker_service="external_api",
       timeout_seconds=10.0,
       fallback_func=lambda: {"status": "service_unavailable"}
   )
   def call_external_service(endpoint, params):
       response = requests.get(endpoint, params=params)
       response.raise_for_status()
       return response.json()

Database Operations
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import with_retry, RetryConfig

   @with_retry(config=RetryConfig(
       max_attempts=3,
       base_delay=0.5,
       retryable_exceptions=[DatabaseConnectionError, TransactionError]
   ))
   def save_user_data(user_data):
       with database.transaction():
           database.save_user(user_data)

File Operations
~~~~~~~~~~~~~~~

.. code-block:: python

   from rabbitmirror.error_recovery import with_fallback, with_retry

   @with_fallback(lambda filename: f"Failed to process {filename}")
   @with_retry(config=RetryConfig(max_attempts=2))
   def process_file(filename):
       with open(filename, 'r') as f:
           return process_data(f.read())
