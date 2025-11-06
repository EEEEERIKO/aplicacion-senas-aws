#!/usr/bin/env bash
# ============================================
# Seed DynamoDB Local with Sample Data
# ============================================

set -e

ENDPOINT_URL="${DYNAMO_ENDPOINT_URL:-http://localhost:4566}"
TABLE_NAME="${DYNAMO_TABLE:-aplicacion-senas-content}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Seeding DynamoDB at ${ENDPOINT_URL}..."
echo "Table: ${TABLE_NAME}"
echo ""

# Generate UUIDs (simplified for bash)
TOPIC_ID="topic-$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo '123e4567-e89b-12d3-a456-426614174000')"
LEVEL_ID="level-$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo 'abc-def-ghi-jkl-mno')"
EXERCISE_ID="exercise-$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo 'ex-001-002-003')"

echo "Generated IDs:"
echo "  Topic: ${TOPIC_ID}"
echo "  Level: ${LEVEL_ID}"
echo "  Exercise: ${EXERCISE_ID}"
echo ""

# 1. Create Languages
echo "Creating languages..."
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "LANG#pt_BR"},
        "SK": {"S": "METADATA"},
        "entity_type": {"S": "language"},
        "code": {"S": "pt_BR"},
        "name": {"S": "Português (Brasil)"},
        "native_name": {"S": "Português"},
        "is_active": {"BOOL": true},
        "created_at": {"S": "'"${TIMESTAMP}"'"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "LANG#en_US"},
        "SK": {"S": "METADATA"},
        "entity_type": {"S": "language"},
        "code": {"S": "en_US"},
        "name": {"S": "English (US)"},
        "native_name": {"S": "English"},
        "is_active": {"BOOL": true},
        "created_at": {"S": "'"${TIMESTAMP}"'"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

echo "✓ Languages created"

# 2. Create Topic
echo "Creating topic..."
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "TOPIC#'"${TOPIC_ID}"'"},
        "SK": {"S": "METADATA"},
        "entity_type": {"S": "topic"},
        "topic_id": {"S": "'"${TOPIC_ID}"'"},
        "slug": {"S": "alphabet"},
        "default_title": {"S": "Alphabet"},
        "order": {"N": "1"},
        "is_published": {"BOOL": true},
        "created_at": {"S": "'"${TIMESTAMP}"'"},
        "updated_at": {"S": "'"${TIMESTAMP}"'"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

# Topic translations
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "TOPIC#'"${TOPIC_ID}"'"},
        "SK": {"S": "LANG#pt_BR"},
        "entity_type": {"S": "topic_translation"},
        "topic_id": {"S": "'"${TOPIC_ID}"'"},
        "language_code": {"S": "pt_BR"},
        "title": {"S": "Alfabeto"},
        "description": {"S": "Aprenda o alfabeto em língua de sinais brasileira"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "TOPIC#'"${TOPIC_ID}"'"},
        "SK": {"S": "LANG#en_US"},
        "entity_type": {"S": "topic_translation"},
        "topic_id": {"S": "'"${TOPIC_ID}"'"},
        "language_code": {"S": "en_US"},
        "title": {"S": "Alphabet"},
        "description": {"S": "Learn the alphabet in sign language"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

echo "✓ Topic created with translations"

# 3. Create Level
echo "Creating level..."
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "TOPIC#'"${TOPIC_ID}"'"},
        "SK": {"S": "LEVEL#'"${LEVEL_ID}"'"},
        "entity_type": {"S": "level"},
        "level_id": {"S": "'"${LEVEL_ID}"'"},
        "topic_id": {"S": "'"${TOPIC_ID}"'"},
        "slug": {"S": "alphabet-1"},
        "position": {"N": "1"},
        "difficulty": {"N": "1"},
        "is_published": {"BOOL": true},
        "metadata": {"M": {
            "estimated_time_minutes": {"N": "10"},
            "min_score_to_pass": {"N": "70"}
        }},
        "created_at": {"S": "'"${TIMESTAMP}"'"},
        "updated_at": {"S": "'"${TIMESTAMP}"'"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

# Level translations
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "LEVEL#'"${LEVEL_ID}"'"},
        "SK": {"S": "LANG#pt_BR"},
        "entity_type": {"S": "level_translation"},
        "level_id": {"S": "'"${LEVEL_ID}"'"},
        "language_code": {"S": "pt_BR"},
        "title": {"S": "Nível 1 - Letras A-E"},
        "description": {"S": "Aprenda as primeiras 5 letras do alfabeto"},
        "hint": {"S": "Observe a posição das mãos e dos dedos"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

echo "✓ Level created with translations"

# 4. Create Exercise
echo "Creating exercise..."
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "LEVEL#'"${LEVEL_ID}"'"},
        "SK": {"S": "EXERCISE#'"${EXERCISE_ID}"'"},
        "entity_type": {"S": "exercise"},
        "exercise_id": {"S": "'"${EXERCISE_ID}"'"},
        "level_id": {"S": "'"${LEVEL_ID}"'"},
        "exercise_type": {"S": "MCQ"},
        "position": {"N": "1"},
        "config": {"M": {
            "time_limit_seconds": {"N": "30"},
            "choices_count": {"N": "4"},
            "points": {"N": "10"}
        }},
        "answer_schema": {"M": {
            "correct_answer_index": {"N": "2"}
        }},
        "created_at": {"S": "'"${TIMESTAMP}"'"},
        "updated_at": {"S": "'"${TIMESTAMP}"'"}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

# Exercise translations
aws dynamodb put-item \
    --table-name ${TABLE_NAME} \
    --item '{
        "PK": {"S": "EXERCISE#'"${EXERCISE_ID}"'"},
        "SK": {"S": "LANG#pt_BR"},
        "entity_type": {"S": "exercise_translation"},
        "exercise_id": {"S": "'"${EXERCISE_ID}"'"},
        "language_code": {"S": "pt_BR"},
        "prompt_text": {"S": "Qual é o sinal para a letra A?"},
        "choice_texts": {"L": [
            {"S": "Opção A"},
            {"S": "Opção B"},
            {"S": "Resposta Correta"},
            {"S": "Opção D"}
        ]},
        "feedback": {"M": {
            "correct": {"S": "Excelente! Este é o sinal correto para a letra A."},
            "incorrect": {"S": "Tente novamente! Observe a posição da mão."}
        }}
    }' \
    --endpoint-url ${ENDPOINT_URL} \
    --region us-east-1 \
    > /dev/null

echo "✓ Exercise created with translations"

echo ""
echo "========================================"
echo "Seed Complete!"
echo "========================================"
echo ""
echo "Sample data created:"
echo "  - 2 Languages (pt_BR, en_US)"
echo "  - 1 Topic (Alphabet) with translations"
echo "  - 1 Level with translations"
echo "  - 1 Exercise (MCQ) with translations"
echo ""
echo "Test IDs:"
echo "  Topic ID: ${TOPIC_ID}"
echo "  Level ID: ${LEVEL_ID}"
echo "  Exercise ID: ${EXERCISE_ID}"
echo ""
echo "To query the data:"
echo "  aws dynamodb scan --table-name ${TABLE_NAME} --endpoint-url ${ENDPOINT_URL}"
echo ""
