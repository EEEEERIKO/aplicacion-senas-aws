"""Levels CRUD endpoints - Public read, Admin write"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from datetime import datetime
from app.core.auth import get_current_admin

router = APIRouter(prefix="/levels", tags=["levels"])

# Pydantic models
class LevelMetadata(BaseModel):
    estimated_time_minutes: Optional[int] = None
    min_score_to_pass: Optional[int] = None
    max_attempts: Optional[int] = None

class LevelTranslationInput(BaseModel):
    title: str
    description: Optional[str] = None
    hint: Optional[str] = None

class LevelCreate(BaseModel):
    topic_id: str
    slug: str
    position: int
    difficulty: int
    metadata: Optional[LevelMetadata] = None
    is_published: bool = False
    translations: Optional[Dict[str, LevelTranslationInput]] = None

class LevelUpdate(BaseModel):
    slug: Optional[str] = None
    position: Optional[int] = None
    difficulty: Optional[int] = None
    metadata: Optional[LevelMetadata] = None
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
@router.get("/topic/{topic_id}")
async def list_levels_by_topic(
    topic_id: str, 
    language: Optional[str] = Query(None),
    published_only: bool = True
):
    """List all levels for a topic (public)"""
    try:
        table = get_dynamodb_table()
        response = table.query(
            IndexName='topic_id-SK-index',
            KeyConditionExpression=Key('topic_id').eq(topic_id) & Key('SK').begins_with('LEVEL#')
        )
        levels = response.get('Items', [])
        
        if published_only:
            levels = [l for l in levels if l.get('is_published', False)]
        
        # Load translations
        if language:
            for level in levels:
                level_id = level.get('level_id')
                if level_id:
                    trans_resp = table.get_item(
                        Key={'PK': f'LEVEL#{level_id}', 'SK': f'LANG#{language}'}
                    )
                    if trans_resp.get('Item'):
                        level['translation'] = trans_resp['Item']
        
        levels.sort(key=lambda x: int(x.get('position', 999)))
        return {"levels": levels, "total": len(levels)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{level_id}")
async def get_level(
    level_id: str,
    topic_id: str = Query(..., description="Parent topic ID"),
    language: Optional[str] = Query(None)
):
    """Get level by ID (public)"""
    try:
        table = get_dynamodb_table()
        response = table.get_item(
            Key={'PK': f'TOPIC#{topic_id}', 'SK': f'LEVEL#{level_id}'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Level not found")
        
        if language:
            trans_resp = table.get_item(
                Key={'PK': f'LEVEL#{level_id}', 'SK': f'LANG#{language}'}
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
async def create_level(
    level_data: LevelCreate,
    current_user: dict = Depends(get_current_admin)
):
    """Create new level (admin only)"""
    try:
        table = get_dynamodb_table()
        
        level_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Main level item
        item = {
            'PK': f'TOPIC#{level_data.topic_id}',
            'SK': f'LEVEL#{level_id}',
            'entity_type': 'level',
            'level_id': level_id,
            'topic_id': level_data.topic_id,
            'slug': level_data.slug,
            'position': str(level_data.position),
            'difficulty': str(level_data.difficulty),
            'is_published': level_data.is_published,
            'created_at': now,
            'updated_at': now,
            'created_by': current_user['user_id']
        }
        
        if level_data.metadata:
            item['metadata'] = level_data.metadata.dict()
        
        table.put_item(Item=item)
        
        # Add translations
        if level_data.translations:
            for lang_code, translation in level_data.translations.items():
                trans_item = {
                    'PK': f'LEVEL#{level_id}',
                    'SK': f'LANG#{lang_code}',
                    'entity_type': 'level_translation',
                    'level_id': level_id,
                    'language_code': lang_code,
                    'title': translation.title,
                }
                if translation.description:
                    trans_item['description'] = translation.description
                if translation.hint:
                    trans_item['hint'] = translation.hint
                
                table.put_item(Item=trans_item)
        
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{level_id}")
async def update_level(
    level_id: str,
    topic_id: str,
    level_data: LevelUpdate,
    current_user: dict = Depends(get_current_admin)
):
    """Update level (admin only)"""
    try:
        table = get_dynamodb_table()
        
        response = table.get_item(
            Key={'PK': f'TOPIC#{topic_id}', 'SK': f'LEVEL#{level_id}'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Level not found")
        
        # Update fields
        if level_data.slug is not None:
            item['slug'] = level_data.slug
        if level_data.position is not None:
            item['position'] = str(level_data.position)
        if level_data.difficulty is not None:
            item['difficulty'] = str(level_data.difficulty)
        if level_data.metadata is not None:
            item['metadata'] = level_data.metadata.dict()
        if level_data.is_published is not None:
            item['is_published'] = level_data.is_published
        
        item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        item['updated_by'] = current_user['user_id']
        
        table.put_item(Item=item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{level_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_level(
    level_id: str,
    topic_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Delete level (admin only)"""
    try:
        table = get_dynamodb_table()
        table.delete_item(Key={'PK': f'TOPIC#{topic_id}', 'SK': f'LEVEL#{level_id}'})
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
