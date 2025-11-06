#!/usr/bin/env bash
# ============================================
# Simple Local Testing with FastAPI + DynamoDB
# No AWS CLI required, uses Python boto3
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================"
echo "Aplicación Señas - Simple Local Setup"
echo -e "========================================${NC}"
echo ""

# Check dependencies
echo "Checking dependencies..."
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker not found. Please install Docker Desktop.${NC}"; exit 1; }
command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Python not found${NC}"; exit 1; }

PYTHON_CMD=$(command -v python3 2>/dev/null || command -v python)
echo -e "${GREEN}✓ Dependencies OK${NC}\n"

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "Project root: $PROJECT_ROOT"
cd "$PROJECT_ROOT"

# Start LocalStack
echo -e "${BLUE}Step 1: Starting LocalStack...${NC}"
cd localstack
docker-compose up -d
echo -e "${GREEN}✓ LocalStack starting${NC}\n"

# Wait for LocalStack
echo "Waiting for LocalStack to be ready (this may take 30-60 seconds)..."
sleep 10

for i in {1..30}; do
    if curl -s http://localhost:4566/_localstack/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ LocalStack is ready${NC}\n"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}Warning: LocalStack may not be fully ready yet, continuing...${NC}\n"
    fi
    sleep 2
done

cd "$PROJECT_ROOT"

# Setup Python environment and run setup script
echo -e "${BLUE}Step 2: Setting up Python environment...${NC}"

cd services/api

# Create venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
fi

# Activate venv
echo "Activating virtual environment..."
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null || . .venv/Scripts/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q boto3 python-dotenv
pip install -q -r requirements.txt

echo -e "${GREEN}✓ Python environment ready${NC}\n"

# Create and run Python setup script
echo -e "${BLUE}Step 3: Creating DynamoDB table and seeding data...${NC}"

cat > setup_dynamo.py << 'PYTHON_SCRIPT'
import boto3
from datetime import datetime
import uuid
import os

# LocalStack endpoint
ENDPOINT_URL = os.environ.get("DYNAMO_ENDPOINT_URL", "http://localhost:4566")
TABLE_NAME = "aplicacion-senas-content"
REGION = "us-east-1"

print(f"Connecting to DynamoDB at {ENDPOINT_URL}...")

# Create DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

# Create table
print(f"Creating table '{TABLE_NAME}'...")
try:
    table = dynamodb.create_table(
        TableName=TABLE_NAME,
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
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print("✓ Table already exists")
    table = dynamodb.Table(TABLE_NAME)

# Seed data
print("\nSeeding sample data...")
now = datetime.utcnow().isoformat() + 'Z'

# Generate IDs
topic_id = str(uuid.uuid4())
level_id = str(uuid.uuid4())
exercise_id = str(uuid.uuid4())

print(f"  Topic ID: {topic_id}")
print(f"  Level ID: {level_id}")
print(f"  Exercise ID: {exercise_id}")

# Languages
print("\nInserting languages...")
table.put_item(Item={
    'PK': 'LANG#pt_BR',
    'SK': 'METADATA',
    'entity_type': 'language',
    'code': 'pt_BR',
    'name': 'Português (Brasil)',
    'native_name': 'Português',
    'is_active': True,
    'created_at': now
})

table.put_item(Item={
    'PK': 'LANG#en_US',
    'SK': 'METADATA',
    'entity_type': 'language',
    'code': 'en_US',
    'name': 'English (US)',
    'native_name': 'English',
    'is_active': True,
    'created_at': now
})
print("✓ Languages created")

# Topic
print("\nInserting topic...")
table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': 'METADATA',
    'entity_type': 'topic',
    'topic_id': topic_id,
    'slug': 'alphabet',
    'default_title': 'Alphabet',
    'order': 1,
    'is_published': True,
    'created_at': now,
    'updated_at': now
})

# Topic translations
table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': 'LANG#pt_BR',
    'entity_type': 'topic_translation',
    'topic_id': topic_id,
    'language_code': 'pt_BR',
    'title': 'Alfabeto',
    'description': 'Aprenda o alfabeto em língua de sinais brasileira'
})

table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': 'LANG#en_US',
    'entity_type': 'topic_translation',
    'topic_id': topic_id,
    'language_code': 'en_US',
    'title': 'Alphabet',
    'description': 'Learn the alphabet in sign language'
})
print("✓ Topic created with translations")

# Level
print("\nInserting level...")
table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': f'LEVEL#{level_id}',
    'entity_type': 'level',
    'level_id': level_id,
    'topic_id': topic_id,
    'slug': 'alphabet-1',
    'position': 1,
    'difficulty': 1,
    'is_published': True,
    'metadata': {
        'estimated_time_minutes': 10,
        'min_score_to_pass': 70
    },
    'created_at': now,
    'updated_at': now
})

# Level translations
table.put_item(Item={
    'PK': f'LEVEL#{level_id}',
    'SK': 'LANG#pt_BR',
    'entity_type': 'level_translation',
    'level_id': level_id,
    'language_code': 'pt_BR',
    'title': 'Nível 1 - Letras A-E',
    'description': 'Aprenda as primeiras 5 letras do alfabeto',
    'hint': 'Observe a posição das mãos e dos dedos'
})
print("✓ Level created with translations")

# Exercise
print("\nInserting exercise...")
table.put_item(Item={
    'PK': f'LEVEL#{level_id}',
    'SK': f'EXERCISE#{exercise_id}',
    'entity_type': 'exercise',
    'exercise_id': exercise_id,
    'level_id': level_id,
    'exercise_type': 'MCQ',
    'position': 1,
    'config': {
        'time_limit_seconds': 30,
        'choices_count': 4,
        'points': 10
    },
    'answer_schema': {
        'correct_answer_index': 2
    },
    'created_at': now,
    'updated_at': now
})

# Exercise translation
table.put_item(Item={
    'PK': f'EXERCISE#{exercise_id}',
    'SK': 'LANG#pt_BR',
    'entity_type': 'exercise_translation',
    'exercise_id': exercise_id,
    'language_code': 'pt_BR',
    'prompt_text': 'Qual é o sinal para a letra A?',
    'choice_texts': ['Opção A', 'Opção B', 'Resposta Correta', 'Opção D'],
    'feedback': {
        'correct': 'Excelente! Este é o sinal correto para a letra A.',
        'incorrect': 'Tente novamente! Observe a posição da mão.'
    }
})
print("✓ Exercise created with translations")

print("\n" + "="*50)
print("Setup Complete!")
print("="*50)
print(f"\nSample data created:")
print(f"  - 2 Languages (pt_BR, en_US)")
print(f"  - 1 Topic (Alphabet) with translations")
print(f"  - 1 Level with translations")
print(f"  - 1 Exercise (MCQ) with translations")
print(f"\nTable: {TABLE_NAME}")
print(f"Endpoint: {ENDPOINT_URL}")
print(f"\nYou can now start the FastAPI server!")
PYTHON_SCRIPT

# Run the setup script
export DYNAMO_ENDPOINT_URL=http://localhost:4566
$PYTHON_CMD setup_dynamo.py

echo -e "${GREEN}✓ DynamoDB setup complete${NC}\n"

# Create .env file
echo -e "${BLUE}Step 4: Creating .env file...${NC}"
cat > .env << 'ENV_FILE'
# Local Development Environment
ENVIRONMENT=development

# DynamoDB Local (LocalStack)
DYNAMO_TABLE=aplicacion-senas-content
DYNAMO_ENDPOINT_URL=http://localhost:4566
DYNAMO_REGION=us-east-1

# S3 Local (LocalStack)
S3_BUCKET=aplicacion-senas-assets-local
S3_ENDPOINT_URL=http://localhost:4566

# AWS Credentials (LocalStack fake credentials)
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_DEFAULT_REGION=us-east-1

# Security
SECRET_KEY=dev-secret-key-change-in-production

# Database (SQLite for local)
DATABASE_URL=sqlite:///./dev.db
ENV_FILE

echo -e "${GREEN}✓ .env file created${NC}\n"

# Start FastAPI server
echo -e "${BLUE}Step 5: Starting FastAPI server...${NC}"
echo -e "${YELLOW}Server will start on http://localhost:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

sleep 2

echo -e "${GREEN}========================================"
echo "All Set! Starting FastAPI..."
echo -e "========================================${NC}\n"

echo -e "Access points:"
echo -e "  ${GREEN}API Docs:${NC} http://localhost:8000/docs"
echo -e "  ${GREEN}Health:${NC}   http://localhost:8000/healthz"
echo -e "  ${GREEN}Root:${NC}     http://localhost:8000/"
echo ""

# Start uvicorn
$PYTHON_CMD -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
