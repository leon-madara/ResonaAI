# TLS 1.3 Configuration Documentation

## Overview

This document describes the TLS (Transport Layer Security) configuration for the ResonaAI Mental Health Platform. The platform uses TLS 1.3 as the primary protocol for encrypting data in transit, with TLS 1.2 as a fallback for compatibility.

## TLS Version Requirements

| Protocol | Status | Notes |
|----------|--------|-------|
| TLS 1.3 | **Required** | Primary protocol, best security |
| TLS 1.2 | Allowed | Fallback for older clients |
| TLS 1.1 | **Disabled** | Deprecated, security vulnerabilities |
| TLS 1.0 | **Disabled** | Deprecated, security vulnerabilities |
| SSL 3.0 | **Disabled** | Broken, POODLE vulnerability |

## Cipher Suites

### TLS 1.3 Cipher Suites (in order of preference)

1. **TLS_AES_256_GCM_SHA384**
   - 256-bit AES-GCM encryption
   - SHA-384 for authentication
   - Highest security option

2. **TLS_CHACHA20_POLY1305_SHA256**
   - ChaCha20 stream cipher with Poly1305 authenticator
   - Excellent for mobile devices
   - Strong security without AES hardware acceleration

3. **TLS_AES_128_GCM_SHA256**
   - 128-bit AES-GCM encryption
   - SHA-256 for authentication
   - Good balance of security and performance

### TLS 1.2 Cipher Suites (fallback)

```
ECDHE-ECDSA-AES256-GCM-SHA384
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-ECDSA-CHACHA20-POLY1305
ECDHE-RSA-CHACHA20-POLY1305
ECDHE-ECDSA-AES128-GCM-SHA256
ECDHE-RSA-AES128-GCM-SHA256
```

All TLS 1.2 ciphers use:
- ECDHE for key exchange (Perfect Forward Secrecy)
- AEAD ciphers only (GCM or POLY1305)
- No CBC mode ciphers (vulnerable to BEAST, Lucky13)

## ECDH Curves

- **X25519** (preferred) - Modern curve, resistant to timing attacks
- **secp384r1** (fallback) - NIST P-384 curve

## Session Configuration

| Setting | Value | Reason |
|---------|-------|--------|
| Session Timeout | 1 day | Balance between performance and security |
| Session Cache | 50MB shared | Improves performance for returning clients |
| Session Tickets | Disabled | Ensures forward secrecy |

## OCSP Stapling

OCSP (Online Certificate Status Protocol) Stapling is enabled to:
- Improve connection performance
- Protect user privacy (client doesn't need to contact CA)
- Ensure certificate revocation is checked

## Nginx Configuration

The TLS configuration is in `/nginx/nginx.conf`:

```nginx
# TLS Protocol Versions
ssl_protocols TLSv1.2 TLSv1.3;

# Cipher Suites
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

# Server preference
ssl_prefer_server_ciphers on;

# ECDH Curve
ssl_ecdh_curve X25519:secp384r1;

# Session configuration
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:50m;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
```

## Security Headers

The following security headers are added to all HTTPS responses:

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | max-age=31536000; includeSubDomains; preload | Force HTTPS for 1 year |
| X-Frame-Options | SAMEORIGIN | Prevent clickjacking |
| X-Content-Type-Options | nosniff | Prevent MIME type sniffing |
| X-XSS-Protection | 1; mode=block | XSS protection (legacy browsers) |
| Referrer-Policy | strict-origin-when-cross-origin | Control referrer information |
| Content-Security-Policy | (see nginx.conf) | Prevent XSS, injection attacks |
| Permissions-Policy | (see nginx.conf) | Control browser features |

## Certificate Requirements

- **Key Type**: RSA 2048-bit minimum, ECDSA P-256 preferred
- **Signature Algorithm**: SHA-256 or better
- **Certificate Chain**: Full chain must be served
- **Validity**: Maximum 398 days (industry standard)

## Verification

### Using the Verification Script

```bash
./scripts/verify_tls.sh mentalhealth.ke 443
```

### Manual Verification with OpenSSL

```bash
# Check TLS 1.3 support
openssl s_client -connect mentalhealth.ke:443 -tls1_3

# Check TLS 1.2 support
openssl s_client -connect mentalhealth.ke:443 -tls1_2

# Verify TLS 1.1 is disabled (should fail)
openssl s_client -connect mentalhealth.ke:443 -tls1_1

# Check cipher negotiation
openssl s_client -connect mentalhealth.ke:443 -cipher 'ECDHE+AESGCM'
```

### SSL Labs Test

For comprehensive testing, use [SSL Labs](https://www.ssllabs.com/ssltest/):

1. Navigate to https://www.ssllabs.com/ssltest/
2. Enter the domain name
3. Check for A+ rating

**Expected Results:**
- Overall Rating: A+
- Certificate: 100%
- Protocol Support: 100%
- Key Exchange: 90%+
- Cipher Strength: 90%+

## Compliance

This TLS configuration meets the requirements of:

- **GDPR** - Data protection during transmission
- **Kenya DPA 2019** - Appropriate technical measures
- **PCI DSS 3.2.1** - TLS 1.2 minimum requirement
- **NIST SP 800-52 Rev 2** - TLS implementation guidance
- **OWASP TLS Guidelines** - Security best practices

## Troubleshooting

### Certificate Issues

```bash
# Check certificate validity
openssl x509 -in /etc/nginx/ssl/fullchain.pem -text -noout

# Verify certificate chain
openssl verify -CAfile /etc/nginx/ssl/chain.pem /etc/nginx/ssl/fullchain.pem
```

### Connection Issues

```bash
# Test from client perspective
curl -v https://mentalhealth.ke/health

# Check nginx error logs
tail -f /var/log/nginx/error.log
```

### Cipher Mismatch

If clients cannot connect:
1. Check client TLS version support
2. Verify cipher suite compatibility
3. Consider adding fallback ciphers for older clients

## Certificate Renewal

Certificates should be renewed before expiration:

```bash
# Using Let's Encrypt / Certbot
certbot renew --quiet

# Test renewal without changes
certbot renew --dry-run
```

Set up automatic renewal:

```bash
# Add to crontab
0 0 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx
```

## References

- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [NIST SP 800-52 Rev 2](https://csrc.nist.gov/publications/detail/sp/800-52/rev-2/final)
- [OWASP TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
- [RFC 8446 - TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446)

