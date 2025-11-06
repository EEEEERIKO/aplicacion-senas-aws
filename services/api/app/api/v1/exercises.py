"""Exercises CRUD endpoints - Public read, Admin write"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from enum import Enum
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from datetime import datetime
from app.core.auth import get_current_admin

router = APIRouter(prefix="/exercises", tags=["exercises"])

# Helper function to convert floats to Decimal for DynamoDB
def convert_floats_to_decimal(obj: Any) -> Any:
    """Recursively convert all float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    return obj

# Exercise types enum
class ExerciseType(str, Enum):
    MCQ = "MCQ"  # Multiple choice
    CAMERA_PRODUCE = "CAMERA_PRODUCE"  # Camera detection
    COPY_PRACTICE = "COPY_PRACTICE"  # Copy practice

# Pydantic models
class ExerciseConfig(BaseModel):
    time_limit: Optional[int] = None
    scoring_rules: Optional[Dict] = None
    choices_count: Optional[int] = None
    model_version: Optional[str] = None
    required_confidence: Optional[float] = None

class ExerciseTranslationInput(BaseModel):
    prompt_text: str
    choice_texts: Optional[List[str]] = None  # For MCQ
    feedback_text: Optional[Dict[str, str]] = None  # correct, incorrect, hint

class ExerciseCreate(BaseModel):
    level_id: str
    exercise_type: ExerciseType
    position: int
    config: Optional[ExerciseConfig] = None
    answer_schema: Optional[Dict] = None
    translations: Optional[Dict[str, ExerciseTranslationInput]] = None

class ExerciseUpdate(BaseModel):
    position: Optional[int] = None
    config: Optional[ExerciseConfig] = None
    answer_schema: Optional[Dict] = None

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
@router.get("/level/{level_id}")
async def list_exercises_by_level(
    level_id: str,
    language: Optional[str] = Query(None)
):
    """List all exercises for a level (public)"""
    try:
        table = get_dynamodb_table()
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'LEVEL#{level_id}') & Key('SK').begins_with('EXERCISE#')
        )
        exercises = response.get('Items', [])
        
        # Load translations
        if language:
            for exercise in exercises:
                exercise_id = exercise.get('exercise_id')
                if exercise_id:
                    trans_resp = table.get_item(
                        Key={'PK': f'EXERCISE#{exercise_id}', 'SK': f'LANG#{language}'}
                    )
                    if trans_resp.get('Item'):
                        exercise['translation'] = trans_resp['Item']
        
        exercises.sort(key=lambda x: int(x.get('position', 999)))
        return {"exercises": exercises, "total": len(exercises)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{exercise_id}")
async def get_exercise(
    exercise_id: str,
    level_id: str = Query(..., description="Parent level ID"),
    language: Optional[str] = Query(None)
):
    """Get exercise by ID (public)"""
    try:
        table = get_dynamodb_table()
        response = table.get_item(
            Key={'PK': f'LEVEL#{level_id}', 'SK': f'EXERCISE#{exercise_id}'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Exercise not found")
        
        if language:
            trans_resp = table.get_item(
                Key={'PK': f'EXERCISE#{exercise_id}', 'SK': f'LANG#{language}'}
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
async def create_exercise(
    exercise_data: ExerciseCreate,
    current_user: dict = Depends(get_current_admin)
):
    """Create new exercise (admin only)"""
    try:
        table = get_dynamodb_table()
        
        exercise_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Main exercise item
        item = {
            'PK': f'LEVEL#{exercise_data.level_id}',
            'SK': f'EXERCISE#{exercise_id}',
            'entity_type': 'exercise',
            'exercise_id': exercise_id,
            'level_id': exercise_data.level_id,
            'exercise_type': exercise_data.exercise_type.value,
            'position': str(exercise_data.position),
            'created_at': now,
            'updated_at': now,
            'created_by': current_user['user_id']
        }
        
        if exercise_data.config:
            item['config'] = convert_floats_to_decimal(exercise_data.config.dict(exclude_none=True))
        if exercise_data.answer_schema:
            item['answer_schema'] = convert_floats_to_decimal(exercise_data.answer_schema)
        
        table.put_item(Item=item)
        
        # Add translations
        if exercise_data.translations:
            for lang_code, translation in exercise_data.translations.items():
                trans_item = {
                    'PK': f'EXERCISE#{exercise_id}',
                    'SK': f'LANG#{lang_code}',
                    'entity_type': 'exercise_translation',
                    'exercise_id': exercise_id,
                    'language_code': lang_code,
                    'prompt_text': translation.prompt_text,
                }
                if translation.choice_texts:
                    trans_item['choice_texts'] = translation.choice_texts
                if translation.feedback_text:
                    trans_item['feedback_text'] = translation.feedback_text
                
                table.put_item(Item=trans_item)
        
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{exercise_id}")
async def update_exercise(
    exercise_id: str,
    level_id: str,
    exercise_data: ExerciseUpdate,
    current_user: dict = Depends(get_current_admin)
):
    """Update exercise (admin only)"""
    try:
        table = get_dynamodb_table()
        
        response = table.get_item(
            Key={'PK': f'LEVEL#{level_id}', 'SK': f'EXERCISE#{exercise_id}'}
        )
        item = response.get('Item')
        if not item:
            raise HTTPException(status_code=404, detail="Exercise not found")
        
        # Update fields
        if exercise_data.position is not None:
            item['position'] = str(exercise_data.position)
        if exercise_data.config is not None:
            item['config'] = convert_floats_to_decimal(exercise_data.config.dict(exclude_none=True))
        if exercise_data.answer_schema is not None:
            item['answer_schema'] = convert_floats_to_decimal(exercise_data.answer_schema)
        
        item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
        item['updated_by'] = current_user['user_id']
        
        table.put_item(Item=item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise_id: str,
    level_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Delete exercise (admin only)"""
    try:
        table = get_dynamodb_table()
        table.delete_item(Key={'PK': f'LEVEL#{level_id}', 'SK': f'EXERCISE#{exercise_id}'})
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
