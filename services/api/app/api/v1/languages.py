"""Languages API endpoints"""
from fastapi import APIRouter, HTTPException
import boto3
from boto3.dynamodb.conditions import Key
import os

router = APIRouter(prefix="/languages", tags=["languages"])

def get_dynamodb_table():
    """Get DynamoDB table"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMO_ENDPOINT_URL', 'http://localhost:4566'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
    return dynamodb.Table('aplicacion-senas-content')

@router.get("")
async def list_languages():
    """Get all languages"""
    try:
        table = get_dynamodb_table()
        response = table.query(
            IndexName='entity_type-created_at-index',
            KeyConditionExpression=Key('entity_type').eq('language')
        )
        return {
            "languages": response.get('Items', []),
            "total": len(response.get('Items', []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{code}")
async def get_language(code: str):
    """Get language by code"""
    try:
        table = get_dynamodb_table()
        response = table.get_item(
            Key={'PK': f'LANG#{code}', 'SK': 'METADATA'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Language not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
