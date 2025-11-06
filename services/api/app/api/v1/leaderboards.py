"""Leaderboards endpoints - Global, Topic, and Level rankings"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import boto3
from boto3.dynamodb.conditions import Key
import os

router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])

# Pydantic models
class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    score: float
    rank: int

def get_dynamodb_table():
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('DYNAMO_ENDPOINT_URL', 'http://localhost:4566'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
    return dynamodb.Table('aplicacion-senas-content')

async def calculate_user_scores_for_scope(table, scope_filter: str = None):
    """Calculate and aggregate user scores for leaderboard"""
    # Query all progress records
    if scope_filter:
        response = table.scan(
            FilterExpression='entity_type = :et AND begins_with(level_id, :scope)',
            ExpressionAttributeValues={
                ':et': 'user_progress',
                ':scope': scope_filter
            }
        )
    else:
        response = table.scan(
            FilterExpression='entity_type = :et',
            ExpressionAttributeValues={':et': 'user_progress'}
        )
    
    progress_items = response.get('Items', [])
    
    # Aggregate scores by user
    user_scores = {}
    for item in progress_items:
        user_id = item.get('user_id')
        score = float(item.get('best_score', 0))
        
        if user_id in user_scores:
            user_scores[user_id] += score
        else:
            user_scores[user_id] = score
    
    # Get usernames
    leaderboard = []
    for user_id, total_score in user_scores.items():
        # Get user info
        user_response = table.get_item(
            Key={'PK': f'USER#{user_id}', 'SK': 'METADATA'}
        )
        user = user_response.get('Item', {})
        username = user.get('name', 'Unknown User')
        
        leaderboard.append({
            'user_id': user_id,
            'username': username,
            'score': total_score
        })
    
    # Sort by score descending
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    # Add ranks
    for idx, entry in enumerate(leaderboard, 1):
        entry['rank'] = idx
    
    return leaderboard

@router.get("/global", response_model=List[LeaderboardEntry])
async def get_global_leaderboard(
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get global leaderboard (top scores across all topics)"""
    try:
        table = get_dynamodb_table()
        leaderboard = await calculate_user_scores_for_scope(table)
        return leaderboard[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{topic_id}", response_model=List[LeaderboardEntry])
async def get_topic_leaderboard(
    topic_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get leaderboard for a specific topic"""
    try:
        table = get_dynamodb_table()
        
        # Get all levels for this topic to filter progress
        levels_response = table.query(
            KeyConditionExpression=Key('PK').eq(f'TOPIC#{topic_id}') & Key('SK').begins_with('LEVEL#')
        )
        level_ids = [item['SK'].replace('LEVEL#', '') for item in levels_response.get('Items', [])]
        
        if not level_ids:
            return []
        
        # Calculate scores for users who have progress in these levels
        all_progress = []
        for level_id in level_ids:
            progress_response = table.scan(
                FilterExpression='entity_type = :et AND level_id = :lid',
                ExpressionAttributeValues={
                    ':et': 'user_progress',
                    ':lid': level_id
                }
            )
            all_progress.extend(progress_response.get('Items', []))
        
        # Aggregate scores by user
        user_scores = {}
        for item in all_progress:
            user_id = item.get('user_id')
            score = float(item.get('best_score', 0))
            
            if user_id in user_scores:
                user_scores[user_id] += score
            else:
                user_scores[user_id] = score
        
        # Build leaderboard
        leaderboard = []
        for user_id, total_score in user_scores.items():
            user_response = table.get_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'METADATA'}
            )
            user = user_response.get('Item', {})
            username = user.get('name', 'Unknown User')
            
            leaderboard.append({
                'user_id': user_id,
                'username': username,
                'score': total_score
            })
        
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        for idx, entry in enumerate(leaderboard, 1):
            entry['rank'] = idx
        
        return leaderboard[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/level/{level_id}", response_model=List[LeaderboardEntry])
async def get_level_leaderboard(
    level_id: str,
    limit: int = Query(default=50, ge=1, le=100)
):
    """Get leaderboard for a specific level"""
    try:
        table = get_dynamodb_table()
        
        # Get all progress for this level
        progress_response = table.scan(
            FilterExpression='entity_type = :et AND level_id = :lid',
            ExpressionAttributeValues={
                ':et': 'user_progress',
                ':lid': level_id
            }
        )
        
        progress_items = progress_response.get('Items', [])
        
        # Aggregate scores by user
        user_scores = {}
        for item in progress_items:
            user_id = item.get('user_id')
            score = float(item.get('best_score', 0))
            
            if user_id in user_scores:
                user_scores[user_id] += score
            else:
                user_scores[user_id] = score
        
        # Build leaderboard
        leaderboard = []
        for user_id, total_score in user_scores.items():
            user_response = table.get_item(
                Key={'PK': f'USER#{user_id}', 'SK': 'METADATA'}
            )
            user = user_response.get('Item', {})
            username = user.get('name', 'Unknown User')
            
            leaderboard.append({
                'user_id': user_id,
                'username': username,
                'score': total_score
            })
        
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        for idx, entry in enumerate(leaderboard, 1):
            entry['rank'] = idx
        
        return leaderboard[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/rank")
async def get_user_rank(user_id: str, scope: str = "global"):
    """Get a specific user's rank and score
    
    scope can be: global, topic:{topic_id}, level:{level_id}
    """
    try:
        table = get_dynamodb_table()
        
        # Parse scope
        if scope == "global":
            leaderboard = await calculate_user_scores_for_scope(table)
        elif scope.startswith("topic:"):
            topic_id = scope.split(":", 1)[1]
            # Get all levels for topic
            levels_response = table.query(
                KeyConditionExpression=Key('PK').eq(f'TOPIC#{topic_id}') & Key('SK').begins_with('LEVEL#')
            )
            level_ids = [item['SK'].replace('LEVEL#', '') for item in levels_response.get('Items', [])]
            
            all_progress = []
            for level_id in level_ids:
                progress_response = table.scan(
                    FilterExpression='entity_type = :et AND level_id = :lid',
                    ExpressionAttributeValues={':et': 'user_progress', ':lid': level_id}
                )
                all_progress.extend(progress_response.get('Items', []))
            
            user_scores = {}
            for item in all_progress:
                uid = item.get('user_id')
                score = float(item.get('best_score', 0))
                user_scores[uid] = user_scores.get(uid, 0) + score
            
            leaderboard = []
            for uid, total_score in user_scores.items():
                user_response = table.get_item(Key={'PK': f'USER#{uid}', 'SK': 'METADATA'})
                user = user_response.get('Item', {})
                leaderboard.append({
                    'user_id': uid,
                    'username': user.get('name', 'Unknown'),
                    'score': total_score
                })
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            for idx, entry in enumerate(leaderboard, 1):
                entry['rank'] = idx
        elif scope.startswith("level:"):
            level_id = scope.split(":", 1)[1]
            progress_response = table.scan(
                FilterExpression='entity_type = :et AND level_id = :lid',
                ExpressionAttributeValues={':et': 'user_progress', ':lid': level_id}
            )
            
            user_scores = {}
            for item in progress_response.get('Items', []):
                uid = item.get('user_id')
                score = float(item.get('best_score', 0))
                user_scores[uid] = user_scores.get(uid, 0) + score
            
            leaderboard = []
            for uid, total_score in user_scores.items():
                user_response = table.get_item(Key={'PK': f'USER#{uid}', 'SK': 'METADATA'})
                user = user_response.get('Item', {})
                leaderboard.append({
                    'user_id': uid,
                    'username': user.get('name', 'Unknown'),
                    'score': total_score
                })
            leaderboard.sort(key=lambda x: x['score'], reverse=True)
            for idx, entry in enumerate(leaderboard, 1):
                entry['rank'] = idx
        else:
            raise HTTPException(status_code=400, detail="Invalid scope format")
        
        # Find user in leaderboard
        user_entry = next((e for e in leaderboard if e['user_id'] == user_id), None)
        
        if not user_entry:
            return {
                "user_id": user_id,
                "rank": None,
                "score": 0,
                "total_users": len(leaderboard),
                "message": "User has no progress in this scope"
            }
        
        return {
            "user_id": user_id,
            "rank": user_entry['rank'],
            "score": user_entry['score'],
            "total_users": len(leaderboard)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
