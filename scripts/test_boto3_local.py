"""
Small helper to test DynamoDB access locally via boto3.
Set environment variable AWS_ENDPOINT_URL to point to LocalStack (e.g. http://localhost:4566)
"""
import os
import boto3

endpoint = os.getenv('AWS_ENDPOINT_URL')
region = os.getenv('AWS_REGION', 'us-east-1')

if endpoint:
    dynamodb = boto3.resource('dynamodb', region_name=region, endpoint_url=endpoint, aws_access_key_id='test', aws_secret_access_key='test')
else:
    dynamodb = boto3.resource('dynamodb', region_name=region)

table_name = os.getenv('DYNAMODB_TABLE', 'aplicacion-senas-content')
table = dynamodb.Table(table_name)

print(f"Scanning table {table_name} (endpoint={endpoint})...")
resp = table.scan(Limit=10)
items = resp.get('Items', [])
print(f"Found {len(items)} items (showing up to 10):")
for it in items:
    print(it)
