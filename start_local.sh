#!/usr/bin/env bash
set -euo pipefail

echo "Starting LocalStack and guidance..."
cd localstack
docker compose up -d

echo "LocalStack started. Next steps:"
echo "1) Export env vars:"
echo "   export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_REGION=us-east-1"
echo "2) Run seed script: scripts/seed_local_dynamo.sh"
echo "3) Package lambda: cd services/api && ./package_lambda.sh"
echo "4) Terraform plan/apply: cd infra && terraform init && terraform apply -var='use_localstack=true' -auto-approve"
