"""Topics CRUD endpoints - Public read, Admin write"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from datetime import datetime
from app.core.auth import get_current_admin

router = APIRouter(prefix="/topics", tags=["topics"])

# Pydantic models
class TopicTranslationInput(BaseModel):
    title: str
    description: Optional[str] = None

class TopicCreate(BaseModel):
    slug: str
    default_title: str
    order: Optional[int] = None
    is_published: bool = False
    translations: Optional[Dict[str, TopicTranslationInput]] = None

class TopicUpdate(BaseModel):
    slug: Optional[str] = None
    default_title: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None

def get_dynamodb_table():
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMO_ENDPOINT_URL', 'http://localhost:4566'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
    return dynamodb.Table('aplicacion-senas-content')

# PUBLIC ENDPOINTS
@router.get("")
async def list_topics(
    language: Optional[str] = Query(None),
    published_only: bool = True
):
    """List all topics (public)"""
    try:
        table = get_dynamodb_table()
        response = table.query(
            IndexName='entity_type-created_at-index',
            KeyConditionExpression=Key('entity_type').eq('topic')
        )
        topics = response.get('Items', [])
        
        if published_only:
            topics = [t for t in topics if t.get('is_published', False)]
        
        # Load translations
        if language:
            for topic in topics:
                topic_id = topic.get('topic_id')
                if topic_id:
                    trans_resp = table.get_item(
                        Key={'PK': f'TOPIC#{topic_id}', 'SK': f'LANG#{language}'}
                    )
                    if trans_resp.get('Item'):
                        topic['translation'] = trans_resp['Item']
        
        topics.sort(key=lambda x: int(x.get('order', 999)))
        return {"topics": topics, "total": len(topics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{topic_id}")
async def get_topic(topic_id: str, language: Optional[str] = Query(None)):
    """Get topic by ID (public)"""
    try:
        table = get_dynamodb_table()
        response = table.get_item(
            Key={'PK': f'TOPIC#{topic_id}', 'SK': 'METADATA'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        if language:
            trans_resp = table.get_item(
                Key={'PK': f'TOPIC#{topic_id}', 'SK': f'LANG#{language}'}
            )
            if trans_resp.get('Item'):
                item['translation'] = trans_resp['Item']
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ADMIN ENDPOINTS
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_data: TopicCreate,
    current_user: dict = Depends(get_current_admin)
):
    """Create new topic (admin only)"""
    try:
        table = get_dynamodb_table()
        
        topic_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Main topic item
        item = {
            'PK': f'TOPIC#{topic_id}',
            'SK': 'METADATA',
            'entity_type': 'topic',
            'topic_id': topic_id,
            'slug': topic_data.slug,
            'default_title': topic_data.default_title,
            'is_published': topic_data.is_published,
            'created_at': now,
            'updated_at': now,
            'created_by': current_user['user_id']
        }
        
        if topic_data.order is not None:
            item['order'] = str(topic_data.order)
        
        table.put_item(Item=item)
        
        # Add translations
        if topic_data.translations:
            for lang_code, translation in topic_data.translations.items():
                trans_item = {
                    'PK': f'TOPIC#{topic_id}',
                    'SK': f'LANG#{lang_code}',
                    'entity_type': 'topic_translation',
                    'topic_id': topic_id,
                    'language_code': lang_code,
                    'title': translation.title,
                }
                if translation.description:
                    trans_item['description'] = translation.description
                
                table.put_item(Item=trans_item)
        
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{topic_id}")
async def update_topic(
    topic_id: str,
    topic_data: TopicUpdate,
    current_user: dict = Depends(get_current_admin)
):
    """Update topic (admin only)"""
    try:
        table = get_dynamodb_table()
        
        # Get existing topic
        response = table.get_item(
            Key={'PK': f'TOPIC#{topic_id}', 'SK': 'METADATA'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Update fields
        if topic_data.slug is not None:
            item['slug'] = topic_data.slug
        if topic_data.default_title is not None:
            item['default_title'] = topic_data.default_title
        if topic_data.order is not None:
            item['order'] = str(topic_data.order)
        if topic_data.is_published is not None:
            item['is_published'] = topic_data.is_published
        
        item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        item['updated_by'] = current_user['user_id']
        
        table.put_item(Item=item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Delete topic (admin only)"""
    try:
        table = get_dynamodb_table()
        
        # Delete main item
        table.delete_item(Key={'PK': f'TOPIC#{topic_id}', 'SK': 'METADATA'})
        
        # TODO: Delete related translations, levels, exercises
        # In production, implement cascade delete or soft delete
        
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
