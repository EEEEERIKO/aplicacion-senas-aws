#!/usr/bin/env bash
# ============================================
# Local Testing Setup Script
# ============================================
# This script sets up the complete local environment:
# 1. Starts LocalStack (DynamoDB, S3, Lambda, API Gateway)
# 2. Creates DynamoDB table with GSIs
# 3. Seeds sample data
# 4. Packages and deploys Lambda
# 5. Creates API Gateway
# 6. Runs smoke tests
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
LOCALSTACK_ENDPOINT="http://localhost:4566"
TABLE_NAME="aplicacion-senas-content"
S3_BUCKET="aplicacion-senas-assets-local"
LAMBDA_NAME="aplicacion-senas-api"
API_NAME="aplicacion-senas-api-local"

echo -e "${BLUE}========================================"
echo "Aplicación Señas - Local Setup"
echo -e "========================================${NC}"
echo ""

# Check dependencies
echo "Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker not found${NC}"; exit 1; }
command -v aws >/dev/null 2>&1 || { echo -e "${RED}AWS CLI not found${NC}"; exit 1; }
echo -e "${GREEN}✓ Dependencies OK${NC}\n"

# Start LocalStack
echo -e "${BLUE}Step 1: Starting LocalStack...${NC}"
cd localstack
docker-compose up -d
echo -e "${GREEN}✓ LocalStack started${NC}\n"

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
for i in {1..30}; do
    if curl -s ${LOCALSTACK_ENDPOINT}/_localstack/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ LocalStack is ready${NC}\n"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}LocalStack failed to start${NC}"
        exit 1
    fi
    sleep 2
done

# Create DynamoDB table
echo -e "${BLUE}Step 2: Creating DynamoDB table...${NC}"
aws dynamodb create-table \
    --table-name ${TABLE_NAME} \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
        AttributeName=entity_type,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
        AttributeName=topic_id,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --global-secondary-indexes \
        "[
            {
                \"IndexName\": \"entity_type-created_at-index\",
                \"KeySchema\": [
                    {\"AttributeName\":\"entity_type\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"created_at\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            },
            {
                \"IndexName\": \"topic_id-SK-index\",
                \"KeySchema\": [
                    {\"AttributeName\":\"topic_id\",\"KeyType\":\"HASH\"},
                    {\"AttributeName\":\"SK\",\"KeyType\":\"RANGE\"}
                ],
                \"Projection\": {\"ProjectionType\":\"ALL\"}
            }
        ]" \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    2>/dev/null || echo "Table already exists"

echo -e "${GREEN}✓ DynamoDB table created${NC}\n"

# Create S3 bucket
echo -e "${BLUE}Step 3: Creating S3 bucket...${NC}"
aws s3 mb s3://${S3_BUCKET} \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    2>/dev/null || echo "Bucket already exists"

echo -e "${GREEN}✓ S3 bucket created${NC}\n"

# Seed sample data
echo -e "${BLUE}Step 4: Seeding sample data...${NC}"
bash ../scripts/seed_dynamo_local.sh
echo -e "${GREEN}✓ Sample data seeded${NC}\n"

# Package Lambda
echo -e "${BLUE}Step 5: Packaging Lambda function...${NC}"
cd ../services/api
bash package_lambda.sh
echo -e "${GREEN}✓ Lambda packaged${NC}\n"

# Deploy Lambda to LocalStack
echo -e "${BLUE}Step 6: Deploying Lambda to LocalStack...${NC}"
aws lambda create-function \
    --function-name ${LAMBDA_NAME} \
    --runtime python3.11 \
    --handler lambda_handler.handler \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --zip-file fileb://lambda_deployment.zip \
    --environment "Variables={DYNAMO_TABLE=${TABLE_NAME},S3_BUCKET=${S3_BUCKET},DYNAMO_ENDPOINT_URL=${LOCALSTACK_ENDPOINT}}" \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    2>/dev/null || aws lambda update-function-code \
        --function-name ${LAMBDA_NAME} \
        --zip-file fileb://lambda_deployment.zip \
        --endpoint-url ${LOCALSTACK_ENDPOINT} \
        --region us-east-1

echo -e "${GREEN}✓ Lambda deployed${NC}\n"

# Create API Gateway
echo -e "${BLUE}Step 7: Creating API Gateway...${NC}"
API_ID=$(aws apigatewayv2 create-api \
    --name ${API_NAME} \
    --protocol-type HTTP \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    --query 'ApiId' \
    --output text 2>/dev/null || \
    aws apigatewayv2 get-apis \
        --endpoint-url ${LOCALSTACK_ENDPOINT} \
        --region us-east-1 \
        --query "Items[?Name=='${API_NAME}'].ApiId" \
        --output text)

echo "API ID: ${API_ID}"

# Create integration
INTEGRATION_ID=$(aws apigatewayv2 create-integration \
    --api-id ${API_ID} \
    --integration-type AWS_PROXY \
    --integration-uri arn:aws:lambda:us-east-1:000000000000:function:${LAMBDA_NAME} \
    --payload-format-version 2.0 \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    --query 'IntegrationId' \
    --output text 2>/dev/null || echo "")

if [ -z "$INTEGRATION_ID" ]; then
    INTEGRATION_ID=$(aws apigatewayv2 get-integrations \
        --api-id ${API_ID} \
        --endpoint-url ${LOCALSTACK_ENDPOINT} \
        --region us-east-1 \
        --query 'Items[0].IntegrationId' \
        --output text)
fi

echo "Integration ID: ${INTEGRATION_ID}"

# Create route
aws apigatewayv2 create-route \
    --api-id ${API_ID} \
    --route-key '$default' \
    --target "integrations/${INTEGRATION_ID}" \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    2>/dev/null || echo "Route already exists"

# Create stage
aws apigatewayv2 create-stage \
    --api-id ${API_ID} \
    --stage-name '$default' \
    --auto-deploy \
    --endpoint-url ${LOCALSTACK_ENDPOINT} \
    --region us-east-1 \
    2>/dev/null || echo "Stage already exists"

API_ENDPOINT="${LOCALSTACK_ENDPOINT}/restapis/${API_ID}/test/_user_request_"

echo -e "${GREEN}✓ API Gateway created${NC}\n"

# Run smoke tests
echo -e "${BLUE}Step 8: Running smoke tests...${NC}"
echo ""

echo -n "Test 1: Health check... "
if curl -s -f ${API_ENDPOINT}/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
fi

echo -n "Test 2: Root endpoint... "
if curl -s -f ${API_ENDPOINT}/ > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
else
    echo -e "${RED}FAIL${NC}"
fi

echo ""
echo -e "${BLUE}========================================"
echo "Setup Complete!"
echo -e "========================================${NC}"
echo ""
echo -e "${GREEN}API Gateway Endpoint:${NC} ${API_ENDPOINT}"
echo -e "${GREEN}DynamoDB Endpoint:${NC} ${LOCALSTACK_ENDPOINT}"
echo -e "${GREEN}S3 Endpoint:${NC} ${LOCALSTACK_ENDPOINT}"
echo ""
echo -e "${YELLOW}To test the API:${NC}"
echo "  curl ${API_ENDPOINT}/healthz"
echo "  curl ${API_ENDPOINT}/"
echo ""
echo -e "${YELLOW}To view DynamoDB data:${NC}"
echo "  aws dynamodb scan --table-name ${TABLE_NAME} --endpoint-url ${LOCALSTACK_ENDPOINT}"
echo ""
echo -e "${YELLOW}To stop LocalStack:${NC}"
echo "  cd localstack && docker-compose down"
echo ""
