#!/usr/bin/env bash
set -euo pipefail

# Simple script to seed LocalStack DynamoDB with basic tables/items using aws CLI
# Requires AWS CLI v2 configured to point to LocalStack (endpoint-url http://localhost:4566)

TABLE=${DYNAMO_TABLE:-app-content}

echo "Creating table ${TABLE} (if not exists) via aws cli..."
aws dynamodb create-table --table-name ${TABLE} \
  --attribute-definitions AttributeName=PK,AttributeType=S AttributeName=SK,AttributeType=S AttributeName=entity_type,AttributeType=S AttributeName=topic_id,AttributeType=S AttributeName=created_at,AttributeType=S \
  --key-schema AttributeName=PK,KeyType=HASH AttributeName=SK,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes '[{"IndexName":"gsi1-entity-type-created-at","KeySchema":[{"AttributeName":"entity_type","KeyType":"HASH"},{"AttributeName":"created_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},{"IndexName":"gsi2-topic-sortkey","KeySchema":[{"AttributeName":"topic_id","KeyType":"HASH"},{"AttributeName":"SK","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
  --endpoint-url http://localhost:4566 || true

echo "Table ensured (or already existed)."
