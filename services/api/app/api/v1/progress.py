"""User Progress endpoints - Track exercise completion and scores"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict
from enum import Enum
import boto3
from boto3.dynamodb.conditions import Key
import os
import uuid
from datetime import datetime
from app.core.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["user-progress"])

# Progress status enum
class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Pydantic models
class ProgressSubmit(BaseModel):
    exercise_id: str
    level_id: str
    status: ProgressStatus
    score: Optional[float] = None
    data: Optional[Dict] = None  # Extra metadata (time taken, answers, etc)

def get_dynamodb_table():
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMO_ENDPOINT_URL', 'http://localhost:4566'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
    return dynamodb.Table('aplicacion-senas-content')

@router.post("/submit")
async def submit_progress(
    progress_data: ProgressSubmit,
    current_user: dict = Depends(get_current_user)
):
    """Submit exercise progress/completion"""
    try:
        table = get_dynamodb_table()
        user_id = current_user['user_id']
        
        # Check if progress record exists
        progress_key = f'PROGRESS#{progress_data.exercise_id}'
        response = table.get_item(
            Key={'PK': f'USER#{user_id}', 'SK': progress_key}
        )
        
        existing = response.get('Item', {})
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Create or update progress
        item = {
            'PK': f'USER#{user_id}',
            'SK': progress_key,
            'entity_type': 'user_progress',
            'user_id': user_id,
            'exercise_id': progress_data.exercise_id,
            'level_id': progress_data.level_id,
            'status': progress_data.status.value,
            'attempts': int(existing.get('attempts', 0)) + 1,
            'last_attempt_at': now
        }
        
        if progress_data.score is not None:
            item['score'] = str(progress_data.score)
            # Update best score
            if 'best_score' not in existing or float(progress_data.score) > float(existing.get('best_score', 0)):
                item['best_score'] = str(progress_data.score)
            else:
                item['best_score'] = existing.get('best_score')
        
        if progress_data.data:
            item['data'] = progress_data.data
        
        if 'created_at' not in existing:
            item['created_at'] = now
        else:
            item['created_at'] = existing['created_at']
        
        item['updated_at'] = now
        
        table.put_item(Item=item)
        
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/level/{level_id}")
async def get_level_progress(
    level_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user's progress for all exercises in a level"""
    try:
        table = get_dynamodb_table()
        user_id = current_user['user_id']
        
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('PROGRESS#'),
            FilterExpression='level_id = :level_id',
            ExpressionAttributeValues={':level_id': level_id}
        )
        
        progress_items = response.get('Items', [])
        
        # Calculate level completion
        total_exercises = len(progress_items)
        completed = sum(1 for p in progress_items if p.get('status') == 'completed')
        average_score = sum(float(p.get('best_score', 0)) for p in progress_items) / total_exercises if total_exercises > 0 else 0
        
        return {
            "level_id": level_id,
            "progress": progress_items,
            "total_exercises": total_exercises,
            "completed_exercises": completed,
            "completion_percentage": (completed / total_exercises * 100) if total_exercises > 0 else 0,
            "average_score": average_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/exercise/{exercise_id}")
async def get_exercise_progress(
    exercise_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user's progress for a specific exercise"""
    try:
        table = get_dynamodb_table()
        user_id = current_user['user_id']
        
        response = table.get_item(
            Key={'PK': f'USER#{user_id}', 'SK': f'PROGRESS#{exercise_id}'}
        )
        
        item = response.get('Item')
        if not item:
            return {
                "exercise_id": exercise_id,
                "status": "not_started",
                "attempts": 0
            }
        
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_user_summary(
    current_user: dict = Depends(get_current_user)
):
    """Get overall user progress summary"""
    try:
        table = get_dynamodb_table()
        user_id = current_user['user_id']
        
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') & Key('SK').begins_with('PROGRESS#')
        )
        
        progress_items = response.get('Items', [])
        
        total_exercises = len(progress_items)
        completed = sum(1 for p in progress_items if p.get('status') == 'completed')
        total_score = sum(float(p.get('best_score', 0)) for p in progress_items)
        total_attempts = sum(int(p.get('attempts', 0)) for p in progress_items)
        
        return {
            "user_id": user_id,
            "total_exercises_attempted": total_exercises,
            "total_completed": completed,
            "total_score": total_score,
            "total_attempts": total_attempts,
            "completion_rate": (completed / total_exercises * 100) if total_exercises > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
