#!/usr/bin/env bash
set -e

echo "========================================"
echo "Local Backend Testing Suite"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DYNAMO_PORT=8001
API_PORT=8000
DYNAMO_CONTAINER="dynamodb-local-test"
TABLE_NAME="app-content-test"
VENV_DIR=".venv"

# Check dependencies
echo "Checking dependencies..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD=$(command -v python3 || command -v python)
echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    
    # Stop backend if running
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Stop DynamoDB container
    echo "Stopping DynamoDB Local..."
    docker stop $DYNAMO_CONTAINER 2>/dev/null || true
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start DynamoDB Local
echo "Starting DynamoDB Local on port $DYNAMO_PORT..."
docker run -d --rm --name $DYNAMO_CONTAINER \
    -p $DYNAMO_PORT:8000 \
    amazon/dynamodb-local:latest > /dev/null

# Wait for DynamoDB to be ready
echo "Waiting for DynamoDB Local to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:$DYNAMO_PORT > /dev/null 2>&1; then
        echo -e "${GREEN}✓ DynamoDB Local is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: DynamoDB Local failed to start${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Set up Python environment
echo "Setting up Python environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv $VENV_DIR
fi

# Activate virtual environment
source $VENV_DIR/Scripts/activate || source $VENV_DIR/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Set environment variables
export DYNAMO_TABLE=$TABLE_NAME
export DYNAMO_ENDPOINT_URL=http://localhost:$DYNAMO_PORT
export DYNAMO_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export DATABASE_URL=sqlite:///./test.db
export SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")

# Create DynamoDB table and seed data
echo "Creating DynamoDB table and seeding test data..."
$PYTHON_CMD << 'PYTHON_SCRIPT'
import boto3
import uuid
from datetime import datetime, timezone

# Initialize DynamoDB client
dynamodb = boto3.client(
    'dynamodb',
    endpoint_url='http://localhost:8001',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# Create table
try:
    dynamodb.create_table(
        TableName='app-content-test',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'},
            {'AttributeName': 'entity_type', 'AttributeType': 'S'},
            {'AttributeName': 'created_at', 'AttributeType': 'S'},
            {'AttributeName': 'topic_id', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'entity_type-created_at-index',
                'KeySchema': [
                    {'AttributeName': 'entity_type', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'topic_id-SK-index',
                'KeySchema': [
                    {'AttributeName': 'topic_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'SK', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    print("✓ Table created successfully")
except dynamodb.exceptions.ResourceInUseException:
    print("✓ Table already exists")

# Seed test data
topic_id = str(uuid.uuid4())
now = datetime.now(timezone.utc).isoformat()

# Insert test topic
dynamodb.put_item(
    TableName='app-content-test',
    Item={
        'PK': {'S': f'TOPIC#{topic_id}'},
        'SK': {'S': 'METADATA'},
        'entity_type': {'S': 'topic'},
        'topic_id': {'S': topic_id},
        'created_at': {'S': now},
        'title_en': {'S': 'Greetings'},
        'title_pt_BR': {'S': 'Cumprimentos'},
        'description_en': {'S': 'Learn basic greetings'},
        'description_pt_BR': {'S': 'Aprenda cumprimentos básicos'}
    }
)

# Insert test level
level_id = str(uuid.uuid4())
dynamodb.put_item(
    TableName='app-content-test',
    Item={
        'PK': {'S': f'TOPIC#{topic_id}'},
        'SK': {'S': f'LEVEL#{level_id}'},
        'entity_type': {'S': 'level'},
        'topic_id': {'S': topic_id},
        'level_id': {'S': level_id},
        'created_at': {'S': now},
        'sequence': {'N': '1'},
        'title_en': {'S': 'Beginner'},
        'title_pt_BR': {'S': 'Iniciante'}
    }
)

print(f"✓ Test data seeded")
print(f"  Topic ID: {topic_id}")
print(f"  Level ID: {level_id}")

# Save IDs to file for tests
with open('/tmp/test_ids.txt', 'w') as f:
    f.write(f"{topic_id}\n{level_id}")

PYTHON_SCRIPT

echo -e "${GREEN}✓ Database ready${NC}"
echo ""

# Read test IDs
TOPIC_ID=$(head -n 1 /tmp/test_ids.txt)
LEVEL_ID=$(tail -n 1 /tmp/test_ids.txt)

# Start backend
echo "Starting backend on port $API_PORT..."
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port $API_PORT > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:$API_PORT/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: Backend failed to start${NC}"
        echo "Backend logs:"
        cat /tmp/backend.log
        exit 1
    fi
    sleep 1
done
echo ""

# Run tests
echo "========================================"
echo "Running API Tests"
echo "========================================"
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Health check
echo -n "Test 1: GET /healthz ... "
if curl -s -f http://localhost:$API_PORT/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((TESTS_FAILED++))
fi

# Test 2: Readiness check
echo -n "Test 2: GET /readyz ... "
if curl -s -f http://localhost:$API_PORT/readyz > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL${NC}"
    ((TESTS_FAILED++))
fi

# Test 3: Get topic
echo -n "Test 3: GET /v1/dynamo/topics/$TOPIC_ID ... "
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:$API_PORT/v1/dynamo/topics/$TOPIC_ID)
HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL (HTTP $HTTP_CODE)${NC}"
    ((TESTS_FAILED++))
fi

# Test 4: List levels for topic
echo -n "Test 4: GET /v1/dynamo/topics/$TOPIC_ID/levels ... "
RESPONSE=$(curl -s -w "%{http_code}" http://localhost:$API_PORT/v1/dynamo/topics/$TOPIC_ID/levels)
HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL (HTTP $HTTP_CODE)${NC}"
    ((TESTS_FAILED++))
fi

# Test 5: Create new topic
echo -n "Test 5: POST /v1/dynamo/topics ... "
RESPONSE=$(curl -s -w "%{http_code}" -X POST http://localhost:$API_PORT/v1/dynamo/topics \
    -H "Content-Type: application/json" \
    -d '{"title":{"en":"Alphabet","pt_BR":"Alfabeto"},"description":{"en":"Learn alphabet","pt_BR":"Aprenda o alfabeto"}}')
HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}PASS${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}FAIL (HTTP $HTTP_CODE)${NC}"
    ((TESTS_FAILED++))
fi

# Summary
echo ""
echo "========================================"
echo "Test Results"
echo "========================================"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Backend logs:"
    cat /tmp/backend.log
    exit 1
fi
