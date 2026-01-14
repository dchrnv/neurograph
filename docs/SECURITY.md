# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.67.x  | :white_check_mark: |
| < 0.67  | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities to **security@neurograph.dev** (or create a private security advisory on GitHub).

**Please do NOT create public GitHub issues for security vulnerabilities.**

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Time

- We will acknowledge receipt within 48 hours
- We aim to provide an initial assessment within 7 days
- We will keep you informed of our progress

### Disclosure Policy

- We follow coordinated disclosure
- We request 90 days before public disclosure
- We will credit you in the security advisory (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **Always use HTTPS** in production
2. **Change default secrets** in `.env.production`
3. **Enable firewall rules** for production deployments
4. **Keep dependencies updated** (use Dependabot)
5. **Monitor security advisories** on GitHub

### For Contributors

1. **Never commit secrets** to the repository
2. **Use `bandit` for Python security scanning**
3. **Use `cargo audit` for Rust dependency scanning**
4. **Follow secure coding practices** (OWASP Top 10)
5. **Add security tests** for new features

## Automated Security Scanning

This project uses:

- **Dependabot** - Automated dependency updates
- **bandit** - Python security linter
- **cargo audit** - Rust dependency auditing

See `.github/dependabot.yml` for configuration.

## Security Features

NeuroGraph implements multiple security layers:

- JWT-based authentication
- Role-based access control (RBAC)
- API key management with hashing
- Rate limiting
- Input validation
- Secure headers middleware
- Structured logging for security events

For more details, see [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md).

## Contact

- Security Email: security@neurograph.dev
- GitHub Security Advisories: [Create Advisory](https://github.com/dchrnv/neurograph/security/advisories/new)

---

**Last Updated:** 2026-01-12
