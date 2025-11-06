# Database Design - Aplicación Señas

Diseño de base de datos profesional optimizado para rendimiento, escalabilidad y multi-idioma.

## 📋 Contexto de la Aplicación

**Aplicación de Aprendizaje de Lengua de Señas** con:
- 🌍 Multi-idioma (portugués, español, inglés, etc.)
- 📚 Topics → Levels → Exercises (estructura jerárquica)
- 🎥 Assets multimedia (videos, imágenes en S3)
- 📱 Ejercicios interactivos (MCQ, cámara, práctica)
- 🤖 Modelos ML (TensorFlow Lite para reconocimiento)
- 📊 Sistema de progreso y gamificación

---

## 🎯 Decisión de Base de Datos

### Opción 1: DynamoDB (Recomendado para AWS)

**Ventajas:**
- ✅ **Serverless** - No hay que gestionar servidores
- ✅ **Auto-escalable** - Maneja millones de usuarios
- ✅ **Baja latencia** - < 10ms respuestas
- ✅ **Pay-per-use** - Solo pagas lo que usas
- ✅ **Integración nativa** con Lambda, S3, CloudWatch

**Desventajas:**
- ❌ No soporta JOINs (requiere diseño single-table)
- ❌ Queries complejas limitadas
- ❌ Curva de aprendizaje más alta

### Opción 2: Amazon RDS (PostgreSQL/MySQL)

**Ventajas:**
- ✅ SQL familiar con JOINs, foreign keys
- ✅ Queries complejas fáciles
- ✅ Transacciones ACID completas
- ✅ JSONB nativo (PostgreSQL)

**Desventajas:**
- ❌ Requiere gestión de servidor (incluso con RDS)
- ❌ Escalado vertical limitado
- ❌ Mayor costo base

---

## 🏗️ Diseño Single-Table DynamoDB (RECOMENDADO)

### Ventajas del Single-Table Design

- ✅ **1 request = múltiples entidades** (reduce latencia y costo)
- ✅ **Queries eficientes** con GSIs
- ✅ **Escalabilidad infinita**
- ✅ **Menor costo** (menos requests)

### Estructura de la Tabla Principal

**Tabla**: `aplicacion-senas-content`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| PK | String | Partition Key - Entidad principal |
| SK | String | Sort Key - Entidad relacionada |
| entity_type | String | Tipo de entidad (GSI) |
| created_at | String | ISO timestamp (GSI) |
| updated_at | String | ISO timestamp |
| ttl | Number | Opcional para cache |
| data | Map | Datos específicos de la entidad |

---

## 📊 Patrones de Acceso y Keys

### 1. Languages (Idiomas)

**PK**: `LANG#{code}` (e.g., `LANG#pt_BR`, `LANG#en_US`)  
**SK**: `METADATA`  
**entity_type**: `language`

```json
{
  "PK": "LANG#pt_BR",
  "SK": "METADATA",
  "entity_type": "language",
  "code": "pt_BR",
  "name": "Português (Brasil)",
  "native_name": "Português",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Queries:**
- List all languages: GSI `entity_type-created_at-index` WHERE `entity_type = 'language'`

---

### 2. Topics (Temas)

**PK**: `TOPIC#{topic_id}`  
**SK**: `METADATA`  
**entity_type**: `topic`

```json
{
  "PK": "TOPIC#123e4567-e89b-12d3-a456-426614174000",
  "SK": "METADATA",
  "entity_type": "topic",
  "topic_id": "123e4567-e89b-12d3-a456-426614174000",
  "slug": "alphabet",
  "default_title": "Alphabet",
  "order": 1,
  "icon_url": "s3://bucket/topics/alphabet-icon.png",
  "is_published": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Topic Translations:**

**PK**: `TOPIC#{topic_id}`  
**SK**: `LANG#{lang_code}`  
**entity_type**: `topic_translation`

```json
{
  "PK": "TOPIC#123e4567-e89b-12d3-a456-426614174000",
  "SK": "LANG#pt_BR",
  "entity_type": "topic_translation",
  "topic_id": "123e4567-e89b-12d3-a456-426614174000",
  "language_code": "pt_BR",
  "title": "Alfabeto",
  "description": "Aprenda o alfabeto em língua de sinais"
}
```

**Queries:**
- Get topic: `Query` WHERE `PK = 'TOPIC#123'` AND `SK = 'METADATA'`
- Get topic with translations: `Query` WHERE `PK = 'TOPIC#123'` (returns METADATA + all LANG#*)
- List all topics: GSI WHERE `entity_type = 'topic'` ORDER BY `order`

---

### 3. Levels (Níveis)

**PK**: `TOPIC#{topic_id}`  
**SK**: `LEVEL#{level_id}`  
**entity_type**: `level`

```json
{
  "PK": "TOPIC#123e4567-e89b-12d3-a456-426614174000",
  "SK": "LEVEL#abc-def-ghi",
  "entity_type": "level",
  "level_id": "abc-def-ghi",
  "topic_id": "123e4567-e89b-12d3-a456-426614174000",
  "slug": "alphabet-1",
  "position": 1,
  "difficulty": 1,
  "is_published": true,
  "metadata": {
    "estimated_time_minutes": 15,
    "min_score_to_pass": 70,
    "rewards": {
      "xp": 100,
      "coins": 50
    }
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Level Translations:**

**PK**: `LEVEL#{level_id}`  
**SK**: `LANG#{lang_code}`  
**entity_type**: `level_translation`

```json
{
  "PK": "LEVEL#abc-def-ghi",
  "SK": "LANG#pt_BR",
  "entity_type": "level_translation",
  "level_id": "abc-def-ghi",
  "language_code": "pt_BR",
  "title": "Nível 1 - Letras A-E",
  "description": "Aprenda as primeiras 5 letras",
  "hint": "Observe a posição das mãos",
  "success_message": "Parabéns! Você completou o nível 1!"
}
```

**Queries:**
- Get all levels for topic: `Query` WHERE `PK = 'TOPIC#123'` AND `SK begins_with 'LEVEL#'`
- Get specific level: `Query` WHERE `PK = 'LEVEL#abc'` AND `SK = 'METADATA'`
- Get level with translations: `Query` WHERE `PK = 'LEVEL#abc'`

---

### 4. Exercise Types (Tipos de Ejercicio)

**PK**: `EXERCISE_TYPE#{code}`  
**SK**: `METADATA`  
**entity_type**: `exercise_type`

```json
{
  "PK": "EXERCISE_TYPE#MCQ",
  "SK": "METADATA",
  "entity_type": "exercise_type",
  "code": "MCQ",
  "name": "Multiple Choice Question",
  "description": "Choose the correct answer",
  "requires_camera": false,
  "requires_model": false,
  "config_schema": {
    "time_limit": "number",
    "choices_count": "number",
    "randomize_choices": "boolean"
  }
}
```

**Tipos comunes:**
- `MCQ` - Multiple Choice (video → respuesta)
- `CAMERA_PRODUCE` - Grabar seña con cámara
- `CAMERA_RECOGNIZE` - Reconocer seña del usuario
- `COPY_PRACTICE` - Ver video y repetir
- `MATCH_PAIRS` - Emparejar señas con significados
- `FILL_BLANK` - Completar frases

---

### 5. Exercises (Ejercicios)

**PK**: `LEVEL#{level_id}`  
**SK**: `EXERCISE#{exercise_id}`  
**entity_type**: `exercise`

```json
{
  "PK": "LEVEL#abc-def-ghi",
  "SK": "EXERCISE#ex-001",
  "entity_type": "exercise",
  "exercise_id": "ex-001",
  "level_id": "abc-def-ghi",
  "exercise_type": "MCQ",
  "position": 1,
  "config": {
    "time_limit_seconds": 30,
    "choices_count": 4,
    "randomize_choices": true,
    "points": 10
  },
  "answer_schema": {
    "correct_answer_index": 2,
    "correct_answer_id": "choice-c"
  },
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

**Exercise Translations:**

**PK**: `EXERCISE#{exercise_id}`  
**SK**: `LANG#{lang_code}`  
**entity_type**: `exercise_translation`

```json
{
  "PK": "EXERCISE#ex-001",
  "SK": "LANG#pt_BR",
  "entity_type": "exercise_translation",
  "exercise_id": "ex-001",
  "language_code": "pt_BR",
  "prompt_text": "Qual é o sinal para a letra 'A'?",
  "choice_texts": [
    "Opção A",
    "Opção B",
    "Opção C - Correto",
    "Opção D"
  ],
  "feedback": {
    "correct": "Excelente! Este é o sinal correto para 'A'",
    "incorrect": "Não é bem assim. Tente novamente!"
  }
}
```

**Queries:**
- Get all exercises for level: `Query` WHERE `PK = 'LEVEL#abc'` AND `SK begins_with 'EXERCISE#'`
- Get exercise with translations: `Query` WHERE `PK = 'EXERCISE#ex-001'`

---

### 6. Assets (Multimedia S3)

**PK**: `ASSET#{asset_id}`  
**SK**: `METADATA`  
**entity_type**: `asset`

```json
{
  "PK": "ASSET#video-abc-123",
  "SK": "METADATA",
  "entity_type": "asset",
  "asset_id": "video-abc-123",
  "s3_key": "levels/pt_BR/alphabet/level1/example-a.mp4",
  "s3_bucket": "aplicacion-senas-assets",
  "mime_type": "video/mp4",
  "size_bytes": 1048576,
  "duration_seconds": 5.2,
  "language_code": "pt_BR",
  "metadata": {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "thumbnail_key": "levels/pt_BR/alphabet/level1/example-a-thumb.jpg",
    "transcoded_formats": ["720p", "480p", "360p"]
  },
  "version": 1,
  "checksum": "sha256:abc123...",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Exercise Assets (Relación M:N):**

**PK**: `EXERCISE#{exercise_id}`  
**SK**: `ASSET#{asset_id}#{role}`  
**entity_type**: `exercise_asset`

```json
{
  "PK": "EXERCISE#ex-001",
  "SK": "ASSET#video-abc-123#prompt_video",
  "entity_type": "exercise_asset",
  "exercise_id": "ex-001",
  "asset_id": "video-abc-123",
  "role": "prompt_video",
  "s3_key": "levels/pt_BR/alphabet/level1/example-a.mp4",
  "presigned_url_ttl": 3600
}
```

**Roles comunes:**
- `prompt_video` - Video del ejercicio
- `answer_video` - Video de respuesta correcta
- `thumbnail` - Miniatura
- `example` - Video de ejemplo
- `hint_video` - Pista visual

**Queries:**
- Get all assets for exercise: `Query` WHERE `PK = 'EXERCISE#ex-001'` AND `SK begins_with 'ASSET#'`
- Get specific asset: `GetItem` WHERE `PK = 'ASSET#video-abc-123'` AND `SK = 'METADATA'`

---

### 7. ML Models (TensorFlow Lite)

**PK**: `MODEL#{model_id}`  
**SK**: `VERSION#{version}`  
**entity_type**: `ml_model`

```json
{
  "PK": "MODEL#sign-recognizer",
  "SK": "VERSION#2.0.1",
  "entity_type": "ml_model",
  "model_id": "sign-recognizer",
  "name": "Sign Language Recognizer",
  "version": "2.0.1",
  "language_code": "pt_BR",
  "asset_id": "model-tflite-abc",
  "s3_key": "models/sign-recognizer-v2.0.1.tflite",
  "size_bytes": 5242880,
  "checksum": "sha256:def456...",
  "metadata": {
    "input_shape": [1, 224, 224, 3],
    "output_classes": 26,
    "accuracy": 0.95,
    "supported_signs": ["A", "B", "C", "..."]
  },
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Queries:**
- Get latest model version: `Query` WHERE `PK = 'MODEL#sign-recognizer'` ORDER BY `SK DESC` LIMIT 1
- List all models: GSI WHERE `entity_type = 'ml_model'` AND `is_active = true`

---

### 8. Users (Usuarios)

**PK**: `USER#{user_id}`  
**SK**: `METADATA`  
**entity_type**: `user`

```json
{
  "PK": "USER#550e8400-e29b-41d4-a716-446655440000",
  "SK": "METADATA",
  "entity_type": "user",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "name": "João Silva",
  "preferred_language": "pt_BR",
  "profile_image_url": "s3://bucket/users/550e8400/avatar.jpg",
  "subscription_tier": "free",
  "total_xp": 1250,
  "level": 5,
  "streak_days": 7,
  "created_at": "2025-01-01T00:00:00Z",
  "last_active_at": "2025-11-06T10:30:00Z"
}
```

---

### 9. User Progress (Progreso del Usuario)

**PK**: `USER#{user_id}`  
**SK**: `PROGRESS#{level_id}#{exercise_id}`  
**entity_type**: `user_progress`

```json
{
  "PK": "USER#550e8400-e29b-41d4-a716-446655440000",
  "SK": "PROGRESS#abc-def-ghi#ex-001",
  "entity_type": "user_progress",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "level_id": "abc-def-ghi",
  "exercise_id": "ex-001",
  "status": "completed",
  "score": 85,
  "max_score": 100,
  "attempts": 2,
  "time_spent_seconds": 45,
  "last_attempt_at": "2025-11-06T10:25:00Z",
  "data": {
    "answers": [
      {"question_id": 1, "correct": true, "time_ms": 12000},
      {"question_id": 2, "correct": false, "time_ms": 18000}
    ],
    "stars_earned": 2
  },
  "created_at": "2025-11-05T08:00:00Z",
  "updated_at": "2025-11-06T10:25:00Z"
}
```

**Status enum:**
- `not_started` - No iniciado
- `in_progress` - En progreso
- `completed` - Completado con éxito
- `failed` - Fallado (necesita reintentar)

**Queries:**
- Get user progress for level: `Query` WHERE `PK = 'USER#550e8400'` AND `SK begins_with 'PROGRESS#abc-def-ghi#'`
- Get specific exercise progress: `GetItem` WHERE `PK = 'USER#550e8400'` AND `SK = 'PROGRESS#abc-def-ghi#ex-001'`

---

### 10. Level Progress Summary (Agregado)

**PK**: `USER#{user_id}`  
**SK**: `LEVEL_SUMMARY#{level_id}`  
**entity_type**: `level_summary`

```json
{
  "PK": "USER#550e8400-e29b-41d4-a716-446655440000",
  "SK": "LEVEL_SUMMARY#abc-def-ghi",
  "entity_type": "level_summary",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "level_id": "abc-def-ghi",
  "status": "completed",
  "total_exercises": 10,
  "completed_exercises": 10,
  "average_score": 88.5,
  "total_time_seconds": 450,
  "stars_earned": 3,
  "xp_earned": 150,
  "first_attempt_at": "2025-11-05T08:00:00Z",
  "completed_at": "2025-11-06T10:25:00Z",
  "updated_at": "2025-11-06T10:25:00Z"
}
```

---

### 11. Leaderboards (Clasificación)

**PK**: `LEADERBOARD#{scope}#{period}`  
**SK**: `USER#{user_id}`  
**entity_type**: `leaderboard_entry`

```json
{
  "PK": "LEADERBOARD#global#2025-W45",
  "SK": "USER#550e8400-e29b-41d4-a716-446655440000",
  "entity_type": "leaderboard_entry",
  "scope": "global",
  "period": "2025-W45",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "JoaoS",
  "score": 1250,
  "rank": 42,
  "country": "BR",
  "updated_at": "2025-11-06T10:25:00Z"
}
```

**Scopes:**
- `global` - Global
- `topic#{topic_id}` - Por tema
- `country#{code}` - Por país
- `friends#{user_id}` - Entre amigos

**Periods:**
- `2025-W45` - Semanal
- `2025-11` - Mensual
- `all-time` - Histórico

**Queries:**
- Get leaderboard: `Query` WHERE `PK = 'LEADERBOARD#global#2025-W45'` ORDER BY `score DESC`

---

## 🔍 Global Secondary Indexes (GSIs)

### GSI-1: `entity_type-created_at-index`

**Partition Key**: `entity_type`  
**Sort Key**: `created_at`  
**Projection**: ALL

**Use cases:**
- List all topics ordered by creation
- List all levels by creation date
- List all exercises

```javascript
// Get all topics ordered by date
dynamodb.query({
  IndexName: 'entity_type-created_at-index',
  KeyConditionExpression: 'entity_type = :type',
  ExpressionAttributeValues: {
    ':type': 'topic'
  },
  ScanIndexForward: false // Descending
})
```

### GSI-2: `topic_id-position-index`

**Partition Key**: `topic_id`  
**Sort Key**: `position`  
**Projection**: ALL

**Use cases:**
- Get all levels for a topic ordered by position
- Reorder levels

```javascript
// Get all levels for topic ordered by position
dynamodb.query({
  IndexName: 'topic_id-position-index',
  KeyConditionExpression: 'topic_id = :topicId',
  ExpressionAttributeValues: {
    ':topicId': '123e4567-e89b-12d3-a456-426614174000'
  },
  ScanIndexForward: true // Ascending
})
```

### GSI-3: `user_id-updated_at-index`

**Partition Key**: `user_id`  
**Sort Key**: `updated_at`  
**Projection**: ALL

**Use cases:**
- Get recent user activity
- List recent progress updates

---

## 💰 Estimación de Costos DynamoDB

### Escenario: 10,000 usuarios activos/mes

**Assumptions:**
- 1 million reads/month
- 500k writes/month
- 5 GB storage

**Costos mensuales:**
- Read capacity: ~$1.25 (PAY_PER_REQUEST)
- Write capacity: ~$6.25 (PAY_PER_REQUEST)
- Storage: ~$1.25 (5 GB × $0.25/GB)
- **Total: ~$9/mes** 💰

---

## 🚀 Alternativa: PostgreSQL Schema (RDS)

Si prefieres SQL tradicional:

```sql
-- Ver archivo: docs/DATABASE_SCHEMA_SQL.sql
```

---

## 📝 Próximos Pasos

1. ✅ Revisar y aprobar este diseño
2. 🔨 Crear scripts de seed para DynamoDB
3. 🔧 Implementar repositorios en FastAPI
4. 🧪 Tests de integración
5. 🚀 Deploy a AWS

---

## 🤔 Preguntas para Decidir

1. **¿Cuántos usuarios esperas?**
   - < 1,000 → PostgreSQL RDS puede ser más simple
   - > 10,000 → DynamoDB es mejor opción

2. **¿Queries complejas?**
   - Muchos reports/analytics → PostgreSQL
   - Queries simples predecibles → DynamoDB

3. **¿Budget inicial?**
   - Limitado → DynamoDB (pay-per-use)
   - Fijo mensual → RDS (instancia pequeña)

**Mi recomendación**: **DynamoDB** por escalabilidad, costo y simplicidad operativa. 🎯
