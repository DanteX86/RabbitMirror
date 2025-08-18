# Security Framework for RabbitMirror

## Overview

RabbitMirror includes a comprehensive security framework designed to protect against common web application vulnerabilities and ensure secure handling of user data.

## Security Features

### 1. Input Validation and Sanitization

- **XSS Protection**: Automatic detection and blocking of script tags, JavaScript URLs, and data URLs
- **Path Traversal Prevention**: Detection and blocking of path traversal attempts (`../`, `..\\`)
- **Command Injection Prevention**: Blocking of command injection sequences (`;`, `|`, `&`, backticks)
- **Code Injection Prevention**: Detection of `eval()`, `exec()`, and `import` statements
- **String Length Limits**: Configurable maximum string lengths to prevent buffer overflow attacks
- **Control Character Removal**: Automatic removal of dangerous control characters

### 2. File Upload Security

- **Extension Validation**: Whitelist-based file extension checking
- **Filename Sanitization**: Removal of dangerous characters and path components
- **File Size Limits**: Configurable maximum file sizes
- **Path Traversal Protection**: Additional checks for path traversal in filenames
- **Blocked Extensions**: Comprehensive list of dangerous file extensions (exe, bat, sh, js, etc.)

### 3. Rate Limiting

- **Request Rate Limiting**: Configurable limits on requests per time window
- **Per-User Isolation**: Separate rate limits for different users/IPs
- **Sliding Window**: Time-based rate limiting with automatic cleanup
- **Configurable Thresholds**: Environment variable configuration for limits

### 4. Authentication and Credential Security

- **Secure Key Generation**: Cryptographically secure random key generation
- **Key Strength Validation**: Detection and rejection of weak keys
- **Password Hashing**: PBKDF2 with SHA-256 and salt
- **Secret Masking**: Safe display of secrets with masking
- **Constant-Time Comparison**: Protection against timing attacks

### 5. Security Headers

- **X-Content-Type-Options**: `nosniff` to prevent MIME type sniffing
- **X-Frame-Options**: `DENY` to prevent clickjacking
- **X-XSS-Protection**: Browser XSS protection enabled
- **Strict-Transport-Security**: HTTPS enforcement
- **Content-Security-Policy**: Restrictive CSP for script execution
- **Referrer-Policy**: Strict referrer policy

### 6. Security Auditing and Monitoring

- **Event Logging**: Comprehensive logging of security events
- **Severity Classification**: Automatic classification of security events
- **Security Reports**: Detailed security audit reports
- **Real-time Monitoring**: Detection and alerting of security violations

## Configuration

### Environment Variables

```bash
# Rate limiting
RATE_LIMIT_REQUESTS=100          # Requests per window
RATE_LIMIT_WINDOW=3600           # Window size in seconds

# File upload limits
MAX_FILE_SIZE=104857600          # Maximum file size in bytes (100MB)

# Application security
SECRET_KEY=your-secure-key-here  # Application secret key
FLASK_DEBUG=False                # Disable debug mode in production
```

### Security Configuration

The security framework can be configured programmatically:

```python
from rabbitmirror.security import SecurityConfig

config = SecurityConfig()
config.rate_limit_requests = 50
config.max_file_size = 50 * 1024 * 1024  # 50MB
config.allowed_extensions.add('pdf')
config.blocked_extensions.add('jsp')
```

## Usage Examples

### Input Validation

```python
from rabbitmirror.security import input_validator, SecurityError, ValidationError

try:
    # Validate user input
    safe_input = input_validator.validate_string(user_input, "username")

    # Validate filename
    safe_filename = input_validator.validate_filename(uploaded_file.filename)

    # Validate file path
    safe_path = input_validator.validate_path(file_path)

    # Validate JSON data
    safe_data = input_validator.validate_json_data(json_data)

except SecurityError as e:
    # Handle security violations
    logger.error(f"Security violation: {e}")
    return {"error": "Invalid input detected"}

except ValidationError as e:
    # Handle validation errors
    return {"error": f"Validation failed: {e}"}
```

### Rate Limiting

```python
from rabbitmirror.security import rate_limiter

client_ip = request.remote_addr

if not rate_limiter.is_allowed(client_ip):
    return {"error": "Rate limit exceeded"}, 429

# Process request
remaining = rate_limiter.get_remaining_requests(client_ip)
response.headers['X-RateLimit-Remaining'] = str(remaining)
```

### Secret Management

```python
from rabbitmirror.security import secret_manager

# Generate secure key
secure_key = secret_manager.generate_secret_key()

# Validate key strength
if not secret_manager.validate_secret_key(user_key):
    return {"error": "Weak key provided"}

# Hash password
password_hash, salt = secret_manager.hash_secret(password)

# Verify password
if secret_manager.verify_secret(password, stored_hash, stored_salt):
    # Authentication successful
    pass
```

### Security Monitoring

```python
from rabbitmirror.security import security_auditor

# Log security event
security_auditor.log_security_event("suspicious_activity", {
    "user_id": user_id,
    "ip_address": client_ip,
    "action": "multiple_failed_logins"
})

# Generate security report
report = security_auditor.get_security_report()
```

## Security Testing

### Running Security Tests

```bash
# Run all security tests
pytest tests/test_security.py -v

# Run security audit
python security_audit.py

# Check for known vulnerabilities
bandit -r rabbitmirror/
safety check
```

### Security Audit Results

The security audit provides:
- Overall security score
- Test results breakdown
- Vulnerability findings
- Security recommendations
- Detailed JSON report

## Security Best Practices

### 1. Environment Configuration

- **Never use default secret keys in production**
- **Always set `FLASK_DEBUG=False` in production**
- **Use environment variables for sensitive configuration**
- **Regularly rotate secret keys**

### 2. Input Handling

- **Always validate user input**
- **Use parameterized queries for database operations**
- **Sanitize output before rendering**
- **Implement proper error handling**

### 3. File Operations

- **Validate file types and extensions**
- **Use secure file storage locations**
- **Implement file size limits**
- **Scan uploaded files for malware**

### 4. Authentication

- **Use strong password requirements**
- **Implement account lockout policies**
- **Use secure session management**
- **Enable two-factor authentication**

### 5. Monitoring

- **Log all security events**
- **Monitor for suspicious patterns**
- **Set up alerting for security violations**
- **Regularly review security logs**

## Vulnerability Reporting

If you discover a security vulnerability in RabbitMirror, please report it responsibly by:

1. **Do not** disclose the vulnerability publicly
2. Email details to the security team
3. Include steps to reproduce the issue
4. Provide proof of concept if applicable

## Security Updates

- Security patches are released as soon as possible
- Subscribe to security notifications
- Regularly update dependencies
- Monitor security advisories

## Compliance

RabbitMirror's security framework is designed to help with:
- OWASP Top 10 compliance
- Data protection regulations
- Industry security standards
- Security audit requirements

## Security Resources

- [OWASP Security Guidelines](https://owasp.org/)
- [Python Security Best Practices](https://python.guide/writing/security/)
- [Flask Security Considerations](https://flask.palletsprojects.com/en/latest/security/)
- [Web Application Security Testing](https://owasp.org/www-project-web-security-testing-guide/)
