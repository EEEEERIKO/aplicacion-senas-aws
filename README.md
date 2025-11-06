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

Notes
- This is a scaffold for development and testing. Before deploying to production in AWS, review IAM policies, enable encryption at rest for DynamoDB/S3, and configure secrets management.
