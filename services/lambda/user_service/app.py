import os
import json
import boto3
from botocore.exceptions import ClientError

TABLE = os.getenv("DYNAMODB_TABLE", "aplicacion-senas-content")
REGION = os.getenv("AWS_REGION", "us-east-1")

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE)

def lambda_handler(event, context):
    """Simple handler that supports a login-like POST for demonstration.
    Expects JSON body with {"email": "..", "password": ".."} and returns a fake token.
    The function demonstrates using boto3 to read the DynamoDB table.
    """
    try:
        if event.get('requestContext') and event['requestContext'].get('http'):
            # API Gateway v2 payload
            raw_body = event.get('body')
        else:
            raw_body = event.get('body')

        payload = json.loads(raw_body or '{}')
        email = payload.get('email')

        if not email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'email required'})
            }

        # Query DynamoDB for user by email (scan approach for single-table simple demo)
        resp = table.scan(
            FilterExpression = "entity_type = :et and email = :e",
            ExpressionAttributeValues = {':et': 'user', ':e': email}
        )

        items = resp.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'user not found'})
            }

        user = items[0]

        # Return a fake token for demonstration; real project uses JWT
        return {
            'statusCode': 200,
            'body': json.dumps({'access_token': 'local-demo-token', 'user': {'email': user.get('email'), 'role': user.get('role')}})
        }

    except ClientError as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
