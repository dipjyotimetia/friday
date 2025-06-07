# Security Policy

## Supported Versions

We actively support the following versions of FRIDAY with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in FRIDAY, please follow these steps:

### 1. Do NOT Create a Public Issue

Please **do not** report security vulnerabilities through public GitHub issues, discussions, or pull requests.

### 2. Report Privately

Instead, please report security vulnerabilities by:

1. **Email**: Send an email to `dipjyotimetia@gmail.com` with the subject line "FRIDAY Security Vulnerability"
2. **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature at [Security Advisories](https://github.com/dipjyotimetia/friday/security/advisories)

### 3. Include Required Information

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish by exploiting this vulnerability?
- **Reproduction Steps**: Detailed steps to reproduce the issue
- **Affected Components**: Which parts of FRIDAY are affected (CLI, API, Web App, etc.)
- **Environment Details**: Python version, operating system, deployment method
- **Proof of Concept**: Code or screenshots demonstrating the vulnerability (if applicable)
- **Suggested Fix**: If you have ideas for how to fix the issue (optional)

### 4. Response Timeline

We commit to the following response timeline:

- **Initial Response**: Within 48 hours of receiving your report
- **Vulnerability Assessment**: Within 7 days
- **Fix Development**: Within 30 days for critical issues, 60 days for others
- **Public Disclosure**: After fix is released and users have time to update

### 5. Disclosure Process

1. **Private Discussion**: We'll work with you privately to understand and fix the issue
2. **Fix Development**: We'll develop and test a fix
3. **Security Release**: We'll release a new version with the fix
4. **Public Disclosure**: After the fix is available, we'll publish a security advisory
5. **Recognition**: We'll credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices for Users

### Environment Variables
- **Never commit** API keys, tokens, or credentials to version control
- Use the provided `.env.example` template and keep your `.env` file private
- Rotate API keys and tokens regularly
- Use environment-specific credentials (dev, staging, prod)

### Network Security
- Run FRIDAY API behind a reverse proxy (nginx, Apache) in production
- Use HTTPS/TLS for all API communications
- Implement proper firewall rules and network segmentation
- Monitor API access logs for suspicious activity

### Access Control
- Use principle of least privilege for API keys and service accounts
- Regularly review and audit access permissions
- Implement proper authentication and authorization in your deployment
- Use secure storage for credentials (AWS Secrets Manager, Azure Key Vault, etc.)

### Container Security
- Keep Docker images updated with latest security patches
- Scan container images for vulnerabilities using our integrated Trivy scanning
- Use non-root users in container deployments
- Implement proper container resource limits

### Dependency Management
- Regularly update dependencies using `uv sync`
- Monitor security advisories with our automated pip-audit scanning
- Review dependency licenses for compliance
- Use dependency pinning in production deployments

## Security Features

FRIDAY includes several built-in security features:

### Automated Security Scanning
- **Dependency Scanning**: pip-audit integration in CI/CD pipeline
- **Container Scanning**: Trivy vulnerability scanning for Docker images
- **SARIF Integration**: Security results uploaded to GitHub Security tab

### Secure Defaults
- Environment variable configuration (no hardcoded secrets)
- Proper input validation and sanitization
- Secure HTTP headers in API responses
- Rate limiting and request size limits

### Audit Trail
- Comprehensive logging of API requests and CLI operations
- Structured logging with request IDs for traceability
- Error handling that doesn't expose sensitive information

## Scope

This security policy applies to:

- FRIDAY CLI application (`friday` command)
- FRIDAY REST API (FastAPI service)
- FRIDAY Web Application (Next.js frontend)
- Docker containers and deployment configurations
- CI/CD pipeline and build processes

## Security Contact

For security-related questions or concerns:

- **Email**: dipjyotimetia@gmail.com
- **GitHub**: [@dipjyotimetia](https://github.com/dipjyotimetia)
- **Security Advisories**: [GitHub Security](https://github.com/dipjyotimetia/friday/security)

Thank you for helping keep FRIDAY and our community safe!

