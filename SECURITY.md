# Security Guide - Aplicacion Senas AWS

This document outlines security considerations and hardening steps for deploying this open-source project to production AWS infrastructure.

## Critical Security Fixes Applied

### 1. Secrets Management
**Issue**: Hardcoded `SECRET_KEY` in backend config  
**Fix**: Changed to read from environment variable; generates random key if not set (for dev only)  
**Action Required**:
- In production, set `SECRET_KEY` via AWS Secrets Manager or Parameter Store
- Generate strong key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Never commit `.env` files with real secrets to git

### 2. S3 Bucket Security
**Applied**:
- ✅ Server-side encryption (AES256) enabled
- ✅ Public access blocked (all 4 settings)
- ✅ Versioning enabled for data recovery
- ✅ Lifecycle rules for old versions
- ✅ Private ACL enforced

**Production Recommendations**:
- Use KMS Customer Managed Keys (CMK) for encryption
- Enable CloudTrail S3 data events logging
- Add bucket policy to restrict access to specific IAM roles
- Enable MFA delete for critical buckets

### 3. DynamoDB Security
**Applied**:
- ✅ Encryption at rest with AWS managed key
- ✅ Point-in-time recovery enabled
- ✅ Tags for resource management

**Production Recommendations**:
- Use Customer Managed Key (CMK) for encryption
- Enable DynamoDB Streams with encryption
- Set up backup plans with AWS Backup
- Implement fine-grained access control with IAM conditions

### 4. IAM Least Privilege
**Applied**:
- ✅ Lambda role restricted to specific DynamoDB table + indexes
- ✅ S3 access limited to GetObject (read-only for Lambda)
- ✅ CloudWatch logs scoped to specific log group
- ✅ Removed wildcard `Resource: "*"` for logs

**Production Recommendations**:
- Use separate IAM roles per Lambda function
- Add IAM policy conditions (e.g., `aws:SourceIp`, `aws:SecureTransport`)
- Enable CloudTrail for IAM API audit
- Review policies quarterly with IAM Access Analyzer

### 5. API Gateway Hardening
**Applied**:
- ✅ CORS configuration (configurable origins via variable)
- ✅ Access logs to CloudWatch with 7-day retention
- ✅ Throttling: 50 req/sec sustained, 100 burst

**Production Recommendations**:
- Set specific `cors_allowed_origins` (not `*`)
- Add AWS WAF with rate limiting and IP filtering
- Enable AWS Shield Standard (free) or Advanced
- Use API keys or Cognito authorizers for authentication
- Add request/response size limits
- Enable X-Ray tracing for debugging

### 6. Lambda Security
**Current State**: Basic runtime with env vars  
**Production Recommendations**:
- Use Lambda layers for dependencies (reduce package size)
- Set reserved concurrency to prevent runaway costs
- Enable VPC for Lambda if accessing private resources
- Use Secrets Manager for sensitive env vars
- Add dead letter queue (DLQ) for failed invocations
- Enable X-Ray tracing
- Set memory/timeout conservatively (currently 15s timeout is good)

## Open Source Security Checklist

### Before Making Repository Public
- [ ] Remove all `.env` files from git history (use `git filter-branch` or BFG Repo-Cleaner)
- [ ] Add comprehensive `.gitignore` (already added)
- [ ] Scan repo with `git-secrets` or `truffleHog` for leaked credentials
- [ ] Add `SECURITY.md` with vulnerability reporting process (this file)
- [ ] Add `LICENSE` file (recommend MIT or Apache 2.0 for open-source)
- [ ] Document all required environment variables in `.env.example`
- [ ] Add security badges (e.g., Snyk, Dependabot)

### Dependency Security
- [ ] Enable Dependabot alerts on GitHub
- [ ] Run `pip-audit` or `safety check` on Python dependencies
- [ ] Pin exact versions in `requirements.txt` for reproducibility
- [ ] Set up automated dependency updates
- [ ] Review transitive dependencies for known CVEs

### CI/CD Security
- [ ] Store AWS credentials in GitHub Secrets (never in code)
- [ ] Use OIDC for GitHub Actions → AWS (no long-lived credentials)
- [ ] Add SAST (Static Application Security Testing): Bandit, Semgrep
- [ ] Add secret scanning in CI pipeline
- [ ] Require signed commits for production deployments
- [ ] Add branch protection rules (require PR reviews)

### Runtime Security
- [ ] Enable AWS GuardDuty for threat detection
- [ ] Set up AWS Config rules for compliance
- [ ] Use AWS Security Hub for centralized findings
- [ ] Add CloudWatch alarms for anomalous activity
- [ ] Implement log aggregation and SIEM

## Vulnerability Reporting

If you discover a security vulnerability, please:
1. **Do NOT** open a public GitHub issue
2. Email: [YOUR-SECURITY-EMAIL@example.com]
3. Include: description, reproduction steps, impact assessment
4. We will respond within 48 hours

## Security Resources

- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)

## Current Security Posture Summary

✅ **Good**: Encryption enabled, least-privilege IAM, no hardcoded secrets in final version  
⚠️ **Needs Attention**: CORS allows all origins (dev default), no WAF, LocalStack test credentials in docs  
🔴 **Critical for Production**: Replace test credentials, enable WAF, use Secrets Manager, restrict CORS

---

**Last Updated**: 2025-11-06  
**Maintained By**: @EEEEERIKO
