# Aplicacion Senas - AWS scaffold

This repository is a minimal, opinionated scaffold to deploy the Aplicacion Senas backend to AWS using Terraform.

What is included
- Terraform scaffold for: DynamoDB (single-table), S3 (assets), Lambda (FastAPI via Mangum), API Gateway HTTP API, and IAM role templates.
- LocalStack docker-compose for local integration testing (API Gateway, Lambda, DynamoDB, S3 emulated).
- A tiny example FastAPI app with `Mangum` handler that can be packaged as Lambda (in `services/api`).
- Scripts to package the lambda and seed local DynamoDB, plus docs describing the DynamoDB mapping from your relational schema.

Quick start (local with LocalStack)

1. Start LocalStack (from repo root):

```bash
cd localstack
docker compose up -d
```

2. From another shell, export env to point Terraform to LocalStack (or use `-var 'use_localstack=true'`):

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_REGION=us-east-1
```

3. Package the example lambda (optional):

```bash
cd services/api
./package_lambda.sh
```

4. Use Terraform in `infra/` to plan/apply (the project uses a simple scaffold; edit variables as required):

```bash
cd infra
terraform init
terraform plan -var 'use_localstack=true'
terraform apply -var 'use_localstack=true'
```

## 🔒 Security Notice

⚠️ **IMPORTANT**: This repository contains development credentials that are safe for local testing but **MUST BE CHANGED for production**:

### Before Deploying to Production:

1. **Generate a new SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Set this in your production environment (AWS Secrets Manager recommended).

2. **Use real AWS credentials**:
   - Prefer IAM roles for Lambda (no credentials needed)
   - Or set proper AWS credentials via environment variables
   - Never use `test` credentials in production

3. **Review security documentation**:
   - See `services/api/SECURITY.md` for comprehensive security guide
   - See `SECURITY_AUDIT_REPORT.md` for security audit results

### Development Credentials (Safe for Local Testing):
- `AWS_ACCESS_KEY_ID=test` - LocalStack fake credentials
- `AWS_SECRET_ACCESS_KEY=test` - LocalStack fake credentials  
- `SECRET_KEY=dev-secret-key-for-local-testing` - Development only

These credentials **ONLY work with LocalStack** and cannot access real AWS resources.

---

Notes
- This is a scaffold for development and testing. Before deploying to production in AWS, review IAM policies, enable encryption at rest for DynamoDB/S3, and configure secrets management.
