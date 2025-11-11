Infra Terraform scaffold for "aplicacion-senas-aws"

What this creates (minimal):
- S3 bucket for lambda artifacts
- DynamoDB table `aplicacion-senas-content`
- IAM role for Lambdas with DynamoDB access
- Lambda function (user-service) packaged from `services/lambda/user_service`
- API Gateway (HTTP API) with a POST route for `/v1/auth/login` integrated to lambda
- IAM OIDC provider and an IAM role that GitHub Actions can assume (OIDC)

Quick start (local):

1. Install Terraform v1.x and AWS CLI.
2. Configure your AWS credentials (for real deploy):

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_REGION=us-east-1
```

3. Initialize Terraform and plan:

```bash
cd infra/terraform
terraform init
terraform plan -var="github_repo=EEEEERIKO/aplicacion-senas-aws"
```

4. Apply (create infra):

```bash
terraform apply -var="github_repo=EEEEERIKO/aplicacion-senas-aws" -auto-approve
```

Notes:
- The GitHub OIDC thumbprint may need verification for your environment. Replace the thumbprint in `main.tf` if necessary.
- This scaffold is intentionally minimal and designed to be extended into modules by service.
