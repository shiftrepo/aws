# Security Best Practices Guide

## Overview

This document outlines security measures and best practices for the Team Schedule Management System.

## Authentication & Authorization

### Basic Authentication

**Implementation:**
- HTTP Basic Auth with secure credential storage
- Session management with secure cookies
- Password hashing (never store plaintext)

**Configuration:**
```bash
# Strong password requirements
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common dictionary words
- No personal information

# Generate secure password
openssl rand -base64 32
```

**Best Practices:**
1. **Never commit credentials** to version control
2. **Use environment variables** for all secrets
3. **Rotate credentials** regularly (every 90 days)
4. **Unique passwords** per environment
5. **Enable MFA** where possible (future enhancement)

### Session Security

**Configuration:**
```javascript
// Session settings
{
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: true,        // HTTPS only
    httpOnly: true,      // Prevent XSS
    maxAge: 3600000,     // 1 hour
    sameSite: 'strict'   // CSRF protection
  }
}
```

**Recommendations:**
- Session timeout: 1-2 hours for production
- Use secure session storage (Redis for scale)
- Implement session regeneration on login
- Clear sessions on logout

## Data Protection

### Database Security

**SQLite Security Measures:**
1. **File Permissions**
   ```bash
   chmod 600 data/schedule.db  # Read/write for owner only
   chown appuser:appgroup data/schedule.db
   ```

2. **Encryption at Rest** (Optional)
   ```bash
   # Use SQLCipher for encrypted database
   npm install sqlite3-sqlcipher
   ```

3. **Access Control**
   - Database accessible only to application user
   - No direct external access
   - Connection through application layer only

4. **Backup Encryption**
   ```bash
   # Encrypt backups before upload
   gpg --symmetric --cipher-algo AES256 schedule.db
   ```

### Input Validation

**Protect Against:**
- SQL Injection
- XSS (Cross-Site Scripting)
- Command Injection
- Path Traversal

**Implementation:**
```javascript
// Input sanitization
const sanitize = require('sanitize-html');
const validator = require('validator');

// Validate and sanitize all inputs
function validateTeamName(name) {
  if (!name || !validator.isLength(name, { min: 1, max: 100 })) {
    throw new Error('Invalid team name');
  }
  return sanitize(name);
}

// Parameterized queries (prevents SQL injection)
db.prepare('SELECT * FROM teams WHERE id = ?').get(teamId);
```

### Output Encoding

**Prevent XSS:**
```javascript
// HTML encoding
const escapeHtml = require('escape-html');

// JSON responses (automatic encoding)
res.json({ data: escapeHtml(userInput) });
```

## Network Security

### SSL/TLS Configuration

**Production Requirements:**
- TLS 1.2 or higher only
- Strong cipher suites
- Valid SSL certificate
- HSTS enabled

**Nginx SSL Configuration:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Rate Limiting

**Protection Against:**
- Brute force attacks
- DDoS attacks
- API abuse

**Configuration:**
```bash
# Application-level
RATE_LIMIT_MAX=100          # 100 requests
RATE_LIMIT_WINDOW=900000    # per 15 minutes

# Nginx-level
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;
```

**Implementation:**
```javascript
const rateLimit = require('express-rate-limit');

// General API limiter
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  message: 'Too many requests, please try again later'
});

// Stricter limiter for authentication
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: 'Too many login attempts, please try again later'
});
```

### Firewall Configuration

**Recommended Rules:**
```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

## Security Headers

### Required Headers

**Implementation:**
```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  referrerPolicy: { policy: 'no-referrer-when-downgrade' },
  noSniff: true,
  xssFilter: true,
  frameGuard: { action: 'sameorigin' }
}));
```

### Security Headers Checklist

- [x] `Strict-Transport-Security` (HSTS)
- [x] `X-Frame-Options: SAMEORIGIN`
- [x] `X-Content-Type-Options: nosniff`
- [x] `X-XSS-Protection: 1; mode=block`
- [x] `Referrer-Policy: no-referrer-when-downgrade`
- [x] `Content-Security-Policy`
- [x] `Permissions-Policy`

## Logging & Monitoring

### Security Event Logging

**Events to Log:**
1. Authentication attempts (success/failure)
2. Authorization failures
3. Input validation failures
4. Rate limit triggers
5. Unusual activity patterns
6. Database errors
7. Application errors

**Implementation:**
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({
      filename: 'logs/security.log',
      level: 'warn'
    })
  ]
});

// Log security events
logger.warn('Failed login attempt', {
  ip: req.ip,
  username: req.body.username,
  timestamp: new Date()
});
```

### Log Protection

**Best Practices:**
1. **Never log sensitive data** (passwords, tokens, PII)
2. **Rotate logs regularly** (daily/weekly)
3. **Secure log files** (chmod 640)
4. **Monitor for anomalies**
5. **Retain for compliance** (30-90 days)

### Monitoring Alerts

**Configure Alerts For:**
- Multiple failed login attempts
- Unusual traffic patterns
- High error rates
- Resource exhaustion
- Certificate expiration
- Backup failures

## Dependency Management

### Security Scanning

**Regular Audits:**
```bash
# npm audit
npm audit
npm audit fix

# Snyk scanning
npx snyk test
npx snyk monitor

# OWASP Dependency Check
dependency-check --project "Schedule App" --scan .
```

**Automated Scanning:**
- GitHub Dependabot (configured in `.github/dependabot.yml`)
- Snyk GitHub integration
- Weekly security reviews

### Update Policy

1. **Critical vulnerabilities**: Patch within 24 hours
2. **High vulnerabilities**: Patch within 7 days
3. **Medium vulnerabilities**: Patch within 30 days
4. **Low vulnerabilities**: Review and patch in next release

## Backup & Recovery Security

### Backup Security

**Encryption:**
```bash
# Encrypt backups
gpg --symmetric --cipher-algo AES256 schedule.db

# Decrypt for restore
gpg --decrypt schedule.db.gpg > schedule.db
```

**Access Control:**
- Backup files: chmod 600
- Backup scripts: chmod 700
- S3 bucket: Private with IAM policies
- Encryption at rest: Enabled

### Disaster Recovery

**Recovery Procedures:**
1. Validate backup integrity
2. Test restoration process monthly
3. Document recovery steps
4. Maintain offline backups
5. Test recovery time objectives (RTO)

## Compliance Considerations

### Data Privacy

**GDPR Compliance:**
- Data minimization
- Purpose limitation
- Right to erasure
- Data portability
- Consent management

**Implementation:**
```javascript
// Data retention policy
const RETENTION_DAYS = 90;

// Delete old records
db.prepare(`
  DELETE FROM schedules
  WHERE date < datetime('now', '-${RETENTION_DAYS} days')
`).run();

// Export user data
function exportUserData(userId) {
  return {
    teams: db.prepare('SELECT * FROM teams WHERE owner_id = ?').all(userId),
    schedules: db.prepare('SELECT * FROM schedules WHERE user_id = ?').all(userId)
  };
}
```

### Audit Trail

**Requirements:**
- Track all data modifications
- Record user actions
- Maintain immutable logs
- Retention: 1 year minimum

## Security Checklist

### Deployment Checklist

- [ ] Change default credentials
- [ ] Generate strong session secret
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable security headers
- [ ] Configure CORS properly
- [ ] Set up logging and monitoring
- [ ] Enable automated backups
- [ ] Test backup restoration
- [ ] Run security audit
- [ ] Update dependencies
- [ ] Review access controls
- [ ] Configure alerts
- [ ] Document security procedures

### Regular Maintenance

**Weekly:**
- [ ] Review security logs
- [ ] Check for failed login attempts
- [ ] Monitor resource usage
- [ ] Review alerts

**Monthly:**
- [ ] Security audit
- [ ] Dependency updates
- [ ] Backup restoration test
- [ ] Certificate expiry check
- [ ] Performance review

**Quarterly:**
- [ ] Credential rotation
- [ ] Access review
- [ ] Security training
- [ ] Incident response drill
- [ ] Compliance review

## Incident Response

### Response Plan

**1. Detection**
- Monitoring alerts
- User reports
- Security scans

**2. Assessment**
- Severity classification
- Impact analysis
- Scope determination

**3. Containment**
- Isolate affected systems
- Block malicious IPs
- Revoke compromised credentials

**4. Eradication**
- Remove malware/backdoors
- Patch vulnerabilities
- Update security controls

**5. Recovery**
- Restore from clean backups
- Verify system integrity
- Resume operations

**6. Post-Incident**
- Root cause analysis
- Document lessons learned
- Update procedures
- Improve defenses

### Contact Information

**Security Team:**
- Email: security@example.com
- Phone: +1-XXX-XXX-XXXX
- On-call: [PagerDuty/Opsgenie]

## Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **CIS Controls**: https://www.cisecurity.org/controls/
- **Node.js Security**: https://nodejs.org/en/docs/guides/security/

## Updates

This security guide should be reviewed and updated:
- After security incidents
- Quarterly (minimum)
- When adding new features
- When regulations change
