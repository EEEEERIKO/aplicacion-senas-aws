# Query Examples - Aplicación Señas

Ejemplos prácticos de queries para DynamoDB y PostgreSQL.

---

## 🔵 DynamoDB Queries (boto3 - Python)

### Setup

```python
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('aplicacion-senas-content')
```

---

### 1. Languages

#### Get all languages

```python
response = table.query(
    IndexName='entity_type-created_at-index',
    KeyConditionExpression=Key('entity_type').eq('language')
)
languages = response['Items']
```

#### Get specific language

```python
response = table.get_item(
    Key={
        'PK': 'LANG#pt_BR',
        'SK': 'METADATA'
    }
)
language = response.get('Item')
```

---

### 2. Topics

#### List all published topics (ordered)

```python
response = table.query(
    IndexName='entity_type-created_at-index',
    KeyConditionExpression=Key('entity_type').eq('topic'),
    FilterExpression=Attr('is_published').eq(True)
)
topics = sorted(response['Items'], key=lambda x: x.get('order', 0))
```

#### Get topic with all translations

```python
response = table.query(
    KeyConditionExpression=Key('PK').eq('TOPIC#123e4567-e89b-12d3-a456-426614174000')
)

items = response['Items']
topic_metadata = next((item for item in items if item['SK'] == 'METADATA'), None)
translations = [item for item in items if item['SK'].startswith('LANG#')]
```

#### Create new topic

```python
topic_id = str(uuid.uuid4())
now = datetime.utcnow().isoformat()

# Topic metadata
table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': 'METADATA',
    'entity_type': 'topic',
    'topic_id': topic_id,
    'slug': 'numbers',
    'default_title': 'Numbers',
    'order': 2,
    'is_published': True,
    'created_at': now,
    'updated_at': now
})

# Portuguese translation
table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': 'LANG#pt_BR',
    'entity_type': 'topic_translation',
    'topic_id': topic_id,
    'language_code': 'pt_BR',
    'title': 'Números',
    'description': 'Aprenda os números em língua de sinais'
})
```

---

### 3. Levels

#### Get all levels for a topic (ordered by position)

```python
response = table.query(
    KeyConditionExpression=(
        Key('PK').eq('TOPIC#123e4567-e89b-12d3-a456-426614174000') &
        Key('SK').begins_with('LEVEL#')
    )
)
levels = sorted(response['Items'], key=lambda x: x.get('position', 0))
```

#### Get level with translations

```python
level_id = 'abc-def-ghi'

response = table.query(
    KeyConditionExpression=Key('PK').eq(f'LEVEL#{level_id}')
)

items = response['Items']
level_metadata = next((item for item in items if item['SK'] == 'METADATA'), None)
translations = [item for item in items if item['SK'].startswith('LANG#')]
```

#### Create new level

```python
level_id = str(uuid.uuid4())
topic_id = '123e4567-e89b-12d3-a456-426614174000'
now = datetime.utcnow().isoformat()

# Level in TOPIC partition
table.put_item(Item={
    'PK': f'TOPIC#{topic_id}',
    'SK': f'LEVEL#{level_id}',
    'entity_type': 'level',
    'level_id': level_id,
    'topic_id': topic_id,
    'slug': 'numbers-1',
    'position': 1,
    'difficulty': 1,
    'is_published': True,
    'metadata': {
        'estimated_time_minutes': 10,
        'min_score_to_pass': 70
    },
    'created_at': now,
    'updated_at': now
})

# Level translations
table.put_item(Item={
    'PK': f'LEVEL#{level_id}',
    'SK': 'LANG#pt_BR',
    'entity_type': 'level_translation',
    'level_id': level_id,
    'language_code': 'pt_BR',
    'title': 'Números 1-10',
    'description': 'Aprenda os números de 1 a 10',
    'hint': 'Preste atenção na posição dos dedos'
})
```

---

### 4. Exercises

#### Get all exercises for a level

```python
response = table.query(
    KeyConditionExpression=(
        Key('PK').eq('LEVEL#abc-def-ghi') &
        Key('SK').begins_with('EXERCISE#')
    )
)
exercises = sorted(response['Items'], key=lambda x: x.get('position', 0))
```

#### Create MCQ exercise with assets

```python
exercise_id = str(uuid.uuid4())
level_id = 'abc-def-ghi'
now = datetime.utcnow().isoformat()

# Exercise in LEVEL partition
table.put_item(Item={
    'PK': f'LEVEL#{level_id}',
    'SK': f'EXERCISE#{exercise_id}',
    'entity_type': 'exercise',
    'exercise_id': exercise_id,
    'level_id': level_id,
    'exercise_type': 'MCQ',
    'position': 1,
    'config': {
        'time_limit_seconds': 30,
        'choices_count': 4,
        'points': 10
    },
    'answer_schema': {
        'correct_answer_index': 2
    },
    'created_at': now,
    'updated_at': now
})

# Exercise translation
table.put_item(Item={
    'PK': f'EXERCISE#{exercise_id}',
    'SK': 'LANG#pt_BR',
    'entity_type': 'exercise_translation',
    'exercise_id': exercise_id,
    'language_code': 'pt_BR',
    'prompt_text': 'Qual é o sinal para o número 5?',
    'choice_texts': ['Opção A', 'Opção B', 'Opção C - Correto', 'Opção D'],
    'feedback': {
        'correct': 'Excelente! Esse é o sinal correto.',
        'incorrect': 'Tente novamente!'
    }
})

# Link prompt video asset
table.put_item(Item={
    'PK': f'EXERCISE#{exercise_id}',
    'SK': 'ASSET#video-123#prompt_video',
    'entity_type': 'exercise_asset',
    'exercise_id': exercise_id,
    'asset_id': 'video-123',
    'role': 'prompt_video',
    's3_key': 'exercises/pt_BR/numbers/ex-001-prompt.mp4'
})
```

---

### 5. User Progress

#### Get user progress for a level

```python
user_id = '550e8400-e29b-41d4-a716-446655440000'
level_id = 'abc-def-ghi'

response = table.query(
    KeyConditionExpression=(
        Key('PK').eq(f'USER#{user_id}') &
        Key('SK').begins_with(f'PROGRESS#{level_id}#')
    )
)
progress = response['Items']
```

#### Record exercise completion

```python
user_id = '550e8400-e29b-41d4-a716-446655440000'
level_id = 'abc-def-ghi'
exercise_id = 'ex-001'
now = datetime.utcnow().isoformat()

table.put_item(Item={
    'PK': f'USER#{user_id}',
    'SK': f'PROGRESS#{level_id}#{exercise_id}',
    'entity_type': 'user_progress',
    'user_id': user_id,
    'level_id': level_id,
    'exercise_id': exercise_id,
    'status': 'completed',
    'score': 90,
    'max_score': 100,
    'attempts': 1,
    'time_spent_seconds': 25,
    'last_attempt_at': now,
    'data': {
        'answers': [
            {'question_id': 1, 'correct': True, 'time_ms': 10000},
            {'question_id': 2, 'correct': True, 'time_ms': 15000}
        ],
        'stars_earned': 3
    },
    'updated_at': now
})
```

#### Update level summary (aggregation)

```python
# Get all exercise progress for level
response = table.query(
    KeyConditionExpression=(
        Key('PK').eq(f'USER#{user_id}') &
        Key('SK').begins_with(f'PROGRESS#{level_id}#')
    )
)

progress_items = response['Items']
completed = [p for p in progress_items if p['status'] == 'completed']

# Calculate summary
total_exercises = len(progress_items)
completed_exercises = len(completed)
avg_score = sum(p['score'] for p in completed) / len(completed) if completed else 0

# Store summary
table.put_item(Item={
    'PK': f'USER#{user_id}',
    'SK': f'LEVEL_SUMMARY#{level_id}',
    'entity_type': 'level_summary',
    'user_id': user_id,
    'level_id': level_id,
    'status': 'completed' if completed_exercises == total_exercises else 'in_progress',
    'total_exercises': total_exercises,
    'completed_exercises': completed_exercises,
    'average_score': round(avg_score, 2),
    'stars_earned': 3,
    'xp_earned': 150,
    'updated_at': now
})
```

---

### 6. Leaderboards

#### Get global weekly leaderboard

```python
response = table.query(
    KeyConditionExpression=Key('PK').eq('LEADERBOARD#global#2025-W45'),
    ScanIndexForward=False,  # Descending order
    Limit=100
)
leaderboard = response['Items']
```

#### Update leaderboard entry

```python
from datetime import datetime

week = datetime.utcnow().strftime('%Y-W%W')

table.put_item(Item={
    'PK': f'LEADERBOARD#global#{week}',
    'SK': f'USER#{user_id}',
    'entity_type': 'leaderboard_entry',
    'scope': 'global',
    'period': week,
    'user_id': user_id,
    'username': 'JoaoS',
    'score': 1500,
    'rank': 35,
    'updated_at': datetime.utcnow().isoformat()
})
```

---

## 🟢 PostgreSQL Queries (SQL)

### 1. Languages

```sql
-- Get all active languages
SELECT * FROM languages WHERE is_active = true ORDER BY name;

-- Get specific language
SELECT * FROM languages WHERE code = 'pt_BR';
```

---

### 2. Topics

```sql
-- List all published topics with translations
SELECT 
    t.id,
    t.slug,
    t.default_title,
    t."order",
    json_agg(
        json_build_object(
            'language', l.code,
            'title', tt.title,
            'description', tt.description
        )
    ) as translations
FROM topics t
LEFT JOIN topic_translations tt ON t.id = tt.topic_id
LEFT JOIN languages l ON tt.language_id = l.id
WHERE t.is_published = true
GROUP BY t.id, t.slug, t.default_title, t."order"
ORDER BY t."order";

-- Get single topic with Portuguese translation
SELECT 
    t.*,
    tt.title as pt_title,
    tt.description as pt_description
FROM topics t
LEFT JOIN topic_translations tt ON t.id = tt.topic_id
LEFT JOIN languages l ON tt.language_id = l.id
WHERE t.slug = 'alphabet' AND l.code = 'pt_BR';
```

---

### 3. Levels

```sql
-- Get all levels for a topic with translations
SELECT 
    lv.id,
    lv.slug,
    lv.position,
    lv.difficulty,
    lt.title,
    lt.description,
    lt.hint
FROM levels lv
JOIN level_translations lt ON lv.id = lt.level_id
JOIN languages l ON lt.language_id = l.id
WHERE lv.topic_id = 'topic-uuid-here'
  AND l.code = 'pt_BR'
  AND lv.is_published = true
ORDER BY lv.position;

-- Get level with all exercises
SELECT 
    lv.id as level_id,
    lv.slug as level_slug,
    lt.title as level_title,
    e.id as exercise_id,
    e.position as exercise_position,
    et.code as exercise_type,
    ext.prompt_text
FROM levels lv
JOIN level_translations lt ON lv.id = lt.level_id
JOIN exercises e ON lv.id = e.level_id
JOIN exercise_types et ON e.exercise_type_id = et.id
JOIN exercise_translations ext ON e.id = ext.exercise_id
JOIN languages l ON lt.language_id = l.id AND ext.language_id = l.id
WHERE lv.slug = 'alphabet-1' AND l.code = 'pt_BR'
ORDER BY e.position;
```

---

### 4. Exercises

```sql
-- Get exercise with all assets
SELECT 
    e.id as exercise_id,
    et.code as type,
    ext.prompt_text,
    ext.choice_texts,
    ext.feedback,
    json_agg(
        json_build_object(
            'role', ea.role,
            's3_key', a.s3_key,
            'mime_type', a.mime_type,
            'duration', a.duration_seconds
        )
    ) as assets
FROM exercises e
JOIN exercise_types et ON e.exercise_type_id = et.id
JOIN exercise_translations ext ON e.id = ext.exercise_id
LEFT JOIN exercise_assets ea ON e.id = ea.exercise_id
LEFT JOIN assets a ON ea.asset_id = a.id
WHERE e.id = 'exercise-uuid-here'
  AND ext.language_id = (SELECT id FROM languages WHERE code = 'pt_BR')
GROUP BY e.id, et.code, ext.prompt_text, ext.choice_texts, ext.feedback;
```

---

### 5. User Progress

```sql
-- Get user progress summary for topic
SELECT 
    t.slug as topic,
    COUNT(DISTINCT lv.id) as total_levels,
    COUNT(DISTINCT CASE WHEN ls.status = 'completed' THEN ls.level_id END) as completed_levels,
    AVG(ls.average_score) as overall_average,
    SUM(ls.xp_earned) as total_xp
FROM topics t
JOIN levels lv ON t.id = lv.topic_id
LEFT JOIN level_summaries ls ON lv.id = ls.level_id AND ls.user_id = 'user-uuid-here'
WHERE t.id = 'topic-uuid-here'
GROUP BY t.id, t.slug;

-- Get detailed progress for level
SELECT 
    e.position,
    et.code as type,
    ext.prompt_text,
    up.status,
    up.score,
    up.attempts,
    up.last_attempt_at
FROM exercises e
JOIN exercise_types et ON e.exercise_type_id = et.id
JOIN exercise_translations ext ON e.id = ext.exercise_id
LEFT JOIN user_progress up ON e.id = up.exercise_id AND up.user_id = 'user-uuid-here'
WHERE e.level_id = 'level-uuid-here'
  AND ext.language_id = (SELECT id FROM languages WHERE code = 'pt_BR')
ORDER BY e.position;

-- Record exercise completion
INSERT INTO user_progress (
    user_id, exercise_id, level_id, status, score, attempts, 
    time_spent_seconds, last_attempt_at, data
) VALUES (
    'user-uuid',
    'exercise-uuid',
    'level-uuid',
    'completed',
    90,
    1,
    25,
    NOW(),
    '{"answers": [{"correct": true}], "stars": 3}'::jsonb
)
ON CONFLICT (user_id, exercise_id) 
DO UPDATE SET
    status = EXCLUDED.status,
    score = GREATEST(user_progress.score, EXCLUDED.score),
    attempts = user_progress.attempts + 1,
    time_spent_seconds = user_progress.time_spent_seconds + EXCLUDED.time_spent_seconds,
    last_attempt_at = EXCLUDED.last_attempt_at,
    data = EXCLUDED.data,
    updated_at = NOW();
```

---

### 6. Leaderboards

```sql
-- Global leaderboard (top 100)
SELECT 
    u.name,
    u.total_xp,
    u.level,
    RANK() OVER (ORDER BY u.total_xp DESC) as rank
FROM users u
ORDER BY u.total_xp DESC
LIMIT 100;

-- Topic leaderboard
SELECT 
    u.name,
    SUM(ls.xp_earned) as topic_xp,
    COUNT(CASE WHEN ls.status = 'completed' THEN 1 END) as completed_levels,
    RANK() OVER (ORDER BY SUM(ls.xp_earned) DESC) as rank
FROM users u
JOIN level_summaries ls ON u.id = ls.user_id
JOIN levels lv ON ls.level_id = lv.id
WHERE lv.topic_id = 'topic-uuid-here'
GROUP BY u.id, u.name
ORDER BY topic_xp DESC
LIMIT 100;
```

---

## 📊 Performance Comparison

| Operation | DynamoDB | PostgreSQL |
|-----------|----------|------------|
| Get single item | < 10ms | 5-20ms |
| Get topic + translations | ~20ms | 10-30ms |
| Get all exercises for level | ~30ms | 20-50ms |
| Complex aggregations | Need multiple queries | Single query |
| Scalability | Infinite | Limited to instance size |
| Cost (10K users) | ~$10/month | ~$50-100/month |

---

## 🎯 Recomendación Final

Para tu aplicación:

- **Usa DynamoDB** si esperas >10K usuarios y necesitas baja latencia
- **Usa PostgreSQL** si prefieres SQL y tienes <5K usuarios

**Mi recomendación**: **DynamoDB** con el diseño single-table propuesto. 🚀
