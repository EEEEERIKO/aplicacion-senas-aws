# 🔍 Cómo Ver los Datos de LocalStack en la API

## 📋 Guía Paso a Paso

### 1️⃣ Asegúrate de que el Servidor Esté Corriendo

```bash
# Verificar que FastAPI esté corriendo
# Deberías ver: INFO: Uvicorn running on http://127.0.0.1:8000
```

Si no está corriendo:
```bash
cd services/api
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 2️⃣ Abrir Swagger UI

Abre en tu navegador: **http://127.0.0.1:8000/docs**

---

## 3️⃣ Hacer Login para Obtener el Token

### Paso A: Expandir el Endpoint de Login

1. Busca la sección **auth** 
2. Click en **POST /v1/auth/login**
3. Click en **"Try it out"**

### Paso B: Ingresar Credenciales

En el campo "Request body", ingresa:

```json
{
  "email": "erikvalencia445@gmail.com",
  "password": "Erikvalencia1$"
}
```

### Paso C: Ejecutar

1. Click en **"Execute"**
2. Verás una respuesta similar a:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "...",
    "email": "erikvalencia445@gmail.com",
    "name": "Eriko",
    "role": "admin"
  }
}
```

### Paso D: Copiar el Token

Copia el valor de `access_token` (todo el texto largo)

---

## 4️⃣ Autorizar con el Token

### En Swagger UI:

1. **Click en el botón "Authorize" 🔓** (esquina superior derecha)
2. Pega el token en el campo **"Value"**
3. Click en **"Authorize"**
4. Click en **"Close"**

✅ **¡Ahora puedes acceder a todos los endpoints!**

---

## 5️⃣ Ver Datos con la API

### 👥 Ver Todos los Usuarios (Solo Admin)

**Endpoint:** `GET /v1/auth/users`

1. Expande **GET /v1/auth/users**
2. Click **"Try it out"**
3. Click **"Execute"**

**Respuesta:**
```json
[
  {
    "user_id": "ecccc0dc-08d3-4385-a15d-ecb3f0b7c13b",
    "email": "erikvalencia445@gmail.com",
    "name": "Eriko",
    "role": "admin",
    "language_preference": "pt_BR",
    "created_at": "2025-11-06T..."
  }
]
```

---

### 📚 Ver Topics

**Endpoint:** `GET /v1/topics`

1. Expande **GET /v1/topics**
2. Click **"Try it out"**
3. Click **"Execute"**

**Respuesta:**
```json
[
  {
    "topic_id": "...",
    "name": {
      "pt_BR": "Alfabeto",
      "en_US": "Alphabet"
    },
    "description": {
      "pt_BR": "Aprenda as letras do alfabeto em Libras",
      "en_US": "Learn the alphabet letters in Sign Language"
    },
    "icon_url": "https://example.com/icons/alphabet.png",
    "order_index": 1
  },
  {
    "topic_id": "...",
    "name": {
      "pt_BR": "Cumprimentos",
      "en_US": "Greetings"
    },
    ...
  },
  {
    "topic_id": "...",
    "name": {
      "pt_BR": "Números",
      "en_US": "Numbers"
    },
    ...
  }
]
```

---

### 📊 Ver Levels

**Endpoint:** `GET /v1/levels`

1. Expande **GET /v1/levels**
2. Click **"Try it out"**
3. Click **"Execute"**

**Respuesta:**
```json
[
  {
    "level_id": "...",
    "name": {
      "pt_BR": "Iniciante",
      "en_US": "Beginner"
    },
    "difficulty": 1,
    "min_score": 0
  },
  {
    "level_id": "...",
    "name": {
      "pt_BR": "Básico",
      "en_US": "Basic"
    },
    "difficulty": 2,
    "min_score": 100
  },
  ...
]
```

---

### 📝 Ver Exercises

**Endpoint:** `GET /v1/exercises`

1. Expande **GET /v1/exercises**
2. Click **"Try it out"**
3. Puedes filtrar por:
   - `topic_id` - Ver ejercicios de un topic específico
   - `level_id` - Ver ejercicios de un nivel específico
4. Click **"Execute"**

**Respuesta:**
```json
[
  {
    "exercise_id": "...",
    "topic_id": "...",
    "level_id": "...",
    "type": "gesture_recognition",
    "title": {
      "pt_BR": "Letra A",
      "en_US": "Letter A"
    },
    "description": {
      "pt_BR": "Identifique a letra A",
      "en_US": "Identify letter A"
    },
    "video_url": "https://example.com/videos/letter_a.mp4",
    "points": 10
  },
  ...
]
```

---

## 📱 Usando curl (Alternativa)

Si prefieres usar la línea de comandos:

### Login y Obtener Token

```bash
curl -X POST http://127.0.0.1:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erikvalencia445@gmail.com","password":"Erikvalencia1$"}' \
  | python -m json.tool
```

**Guarda el token en una variable:**
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erikvalencia445@gmail.com","password":"Erikvalencia1$"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

### Ver Topics

```bash
curl -X GET http://127.0.0.1:8000/v1/topics \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
```

### Ver Levels

```bash
curl -X GET http://127.0.0.1:8000/v1/levels \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
```

### Ver Exercises

```bash
curl -X GET http://127.0.0.1:8000/v1/exercises \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
```

### Ver Usuarios (Admin Only)

```bash
curl -X GET http://127.0.0.1:8000/v1/auth/users \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool
```

---

## 🎯 Endpoints Disponibles (Resumen)

### 🔓 **Endpoints Públicos** (No requieren token)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/healthz` | Health check |
| POST | `/v1/auth/register` | Registrar nuevo usuario |
| POST | `/v1/auth/login` | Iniciar sesión |

### 🔒 **Endpoints Protegidos** (Requieren token)

| Método | Endpoint | Descripción | Rol Requerido |
|--------|----------|-------------|---------------|
| GET | `/v1/auth/me` | Ver perfil actual | user/admin |
| GET | `/v1/languages` | Listar idiomas | user/admin |
| GET | `/v1/topics` | Listar topics | user/admin |
| GET | `/v1/levels` | Listar niveles | user/admin |
| GET | `/v1/exercises` | Listar ejercicios | user/admin |
| GET | `/v1/progress` | Ver progreso | user/admin |
| GET | `/v1/leaderboards` | Ver rankings | user/admin |

### 👑 **Endpoints Solo Admin**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/v1/auth/users` | Listar usuarios |
| PATCH | `/v1/auth/users/{id}/role` | Cambiar rol de usuario |
| POST | `/v1/topics` | Crear topic |
| PUT | `/v1/topics/{id}` | Actualizar topic |
| DELETE | `/v1/topics/{id}` | Eliminar topic |
| POST | `/v1/levels` | Crear level |
| POST | `/v1/exercises` | Crear exercise |

---

## 🧪 Probar CRUD Completo

### Ejemplo: Crear un Nuevo Topic (Admin)

```bash
curl -X POST http://127.0.0.1:8000/v1/topics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": {
      "pt_BR": "Cores",
      "en_US": "Colors"
    },
    "description": {
      "pt_BR": "Aprenda as cores em Libras",
      "en_US": "Learn colors in Sign Language"
    },
    "icon_url": "https://example.com/icons/colors.png",
    "order_index": 4
  }' | python -m json.tool
```

---

## 📊 Ver Datos Directamente en DynamoDB (Sin API)

Si quieres ver los datos raw en DynamoDB:

```bash
# Ver todos los usuarios
python scripts/check_data.py

# O con Python directamente
python -c "
import boto3
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test')
table = dynamodb.Table('aplicacion-senas-content')
response = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'topic'})
for item in response['Items']:
    print(item['name']['pt_BR'])
"
```

---

## 🐛 Solución de Problemas

### Error 401: Unauthorized

**Causa:** Token inválido o expirado (30 minutos)

**Solución:** Vuelve a hacer login y obtén un nuevo token

### Error 403: Forbidden

**Causa:** No tienes permisos (necesitas rol admin)

**Solución:** Verifica tu rol con `GET /v1/auth/me`

### Error 404: Not Found

**Causa:** El endpoint no existe o la URL está mal

**Solución:** Verifica la URL en http://127.0.0.1:8000/docs

### No se ven datos

**Causa:** Los datos no están cargados en DynamoDB

**Solución:**
```bash
python scripts/check_data.py  # Verificar
python scripts/seed_data_direct.py  # Cargar si es necesario
```

---

## 💡 Consejos

1. **Usa Swagger UI** para explorar la API interactivamente
2. **El token expira en 30 minutos** - guárdalo mientras trabajas
3. **Puedes copiar los comandos curl** desde Swagger UI
4. **Los datos de LocalStack persisten** - no necesitas recargarlos cada vez
5. **Todos los endpoints están documentados** en /docs

---

## 📝 Resumen Visual

```
1. Abrir http://127.0.0.1:8000/docs
2. Login → POST /v1/auth/login → Copiar token
3. Click "Authorize" → Pegar token
4. Explorar endpoints:
   - GET /v1/topics → Ver topics de LocalStack
   - GET /v1/levels → Ver levels de LocalStack
   - GET /v1/exercises → Ver exercises de LocalStack
   - GET /v1/auth/users → Ver usuarios (admin)
```

¡Todos los datos que ves en estos endpoints vienen directamente de LocalStack DynamoDB! 🎉
