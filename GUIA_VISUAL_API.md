# 🎯 GUÍA VISUAL: Ver Datos de LocalStack en la API

## 🚀 Inicio Rápido (3 Pasos Simples)

### ✅ PASO 1: Asegúrate que el Servidor Esté Corriendo

```bash
cd services/api
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Deberías ver:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

---

### ✅ PASO 2: Abre Swagger UI en tu Navegador

Abre: **http://127.0.0.1:8000/docs**

---

### ✅ PASO 3: Sigue Esta Guía Visual

## 📸 Capturas de Pantalla (Paso a Paso)

### 1️⃣ Pantalla Inicial de Swagger

Verás todos los endpoints organizados por categorías:

```
┌─────────────────────────────────────────────────┐
│  Aplicación Señas API                           │
│  Gamified sign language learning API            │
├─────────────────────────────────────────────────┤
│                                                 │
│  🔓 Authorize                      Explore      │
│                                                 │
│  ▼ auth - Authentication endpoints             │
│     POST   /v1/auth/register                    │
│     POST   /v1/auth/login                       │
│     GET    /v1/auth/me                          │
│     GET    /v1/auth/users                       │
│     PATCH  /v1/auth/users/{user_id}/role        │
│                                                 │
│  ▼ topics                                       │
│     GET    /v1/topics                           │
│     POST   /v1/topics                           │
│                                                 │
│  ▼ levels                                       │
│     GET    /v1/levels                           │
│                                                 │
│  ▼ exercises                                    │
│     GET    /v1/exercises                        │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

### 2️⃣ Hacer Login

**A. Click en `POST /v1/auth/login`**

```
▼ POST /v1/auth/login
  Login
  
  [Try it out]  [Cancel]
```

**B. Click en "Try it out"**

**C. Ingresa las credenciales:**

```json
{
  "email": "erikvalencia445@gmail.com",
  "password": "Erikvalencia1$"
}
```

**D. Click en "Execute"**

**E. Verás la respuesta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlcmlrdmFsZW5jaWE0NDVAZ21haWwuY29tIiwiZXhwIjoxNzMwOTIzNDAwfQ.XYZ123...",
  "token_type": "bearer",
  "user": {
    "user_id": "ecccc0dc-08d3-4385-a15d-ecb3f0b7c13b",
    "email": "erikvalencia445@gmail.com",
    "name": "Eriko",
    "role": "admin",
    "language_preference": "pt_BR",
    "created_at": "2025-11-06T19:30:00.000000",
    "updated_at": "2025-11-06T19:30:00.000000"
  }
}
```

**F. COPIA el access_token** (todo el texto largo entre comillas)

---

### 3️⃣ Autorizar con el Token

**A. Click en el botón verde "Authorize" 🔓** (esquina superior derecha)

Verás una ventana emergente:

```
┌──────────────────────────────────┐
│  Available authorizations        │
├──────────────────────────────────┤
│                                  │
│  bearerAuth  (http, Bearer)      │
│                                  │
│  Value: [________________]       │
│                                  │
│  [Authorize]  [Close]            │
│                                  │
└──────────────────────────────────┘
```

**B. Pega el token** en el campo "Value"

**C. Click "Authorize"**

**D. Click "Close"**

✅ **¡Ahora el candado 🔓 cambiará a 🔒 y podrás acceder a todos los endpoints!**

---

### 4️⃣ Ver Topics desde LocalStack

**A. Scroll down hasta encontrar `GET /v1/topics`**

**B. Click en `GET /v1/topics`**

**C. Click "Try it out"**

**D. Click "Execute"**

**E. ¡Verás los datos de LocalStack!**

```json
[
  {
    "PK": "TOPIC#a1b2c3d4-...",
    "SK": "METADATA",
    "entity_type": "topic",
    "topic_id": "a1b2c3d4-...",
    "name": {
      "pt_BR": "Alfabeto",
      "en_US": "Alphabet"
    },
    "description": {
      "pt_BR": "Aprenda as letras do alfabeto em Libras",
      "en_US": "Learn the alphabet letters in Sign Language"
    },
    "icon_url": "https://example.com/icons/alphabet.png",
    "order_index": 1,
    "created_at": "2025-11-06T19:30:00.000000",
    "updated_at": "2025-11-06T19:30:00.000000"
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

🎉 **¡Estos son los datos que están guardados en LocalStack!**

---

### 5️⃣ Ver Levels desde LocalStack

**Mismo proceso:**

1. Click en `GET /v1/levels`
2. Click "Try it out"
3. Click "Execute"

**Resultado:**

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

### 6️⃣ Ver Exercises desde LocalStack

1. Click en `GET /v1/exercises`
2. Click "Try it out"
3. **(Opcional)** Filtra por topic_id o level_id
4. Click "Execute"

**Resultado:**

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

### 7️⃣ Ver Usuarios (Solo Admin)

1. Click en `GET /v1/auth/users`
2. Click "Try it out"
3. Click "Execute"

**Resultado:**

```json
[
  {
    "user_id": "ecccc0dc-08d3-4385-a15d-ecb3f0b7c13b",
    "email": "erikvalencia445@gmail.com",
    "name": "Eriko",
    "role": "admin",
    "language_preference": "pt_BR",
    "created_at": "2025-11-06T19:30:00.000000",
    "updated_at": "2025-11-06T19:30:00.000000"
  }
]
```

---

## 📊 Resumen de Datos Disponibles

| Endpoint | Datos que Verás | Cantidad Actual |
|----------|-----------------|-----------------|
| `GET /v1/topics` | Topics (Alfabeto, Cumprimentos, Números) | ~6 (duplicados) |
| `GET /v1/levels` | Levels (Iniciante, Básico, etc.) | ~8 (duplicados) |
| `GET /v1/exercises` | Exercises (Letra A, Olá, etc.) | ~4 (duplicados) |
| `GET /v1/auth/users` | Usuarios del sistema | ~2 (duplicados) |
| `GET /v1/languages` | Idiomas soportados | 2 (pt_BR, en_US) |

---

## 🎨 Códigos de Respuesta HTTP

| Código | Significado | Qué Hacer |
|--------|-------------|-----------|
| 200 OK | ✅ Éxito | Los datos están en el "Response body" |
| 401 Unauthorized | ❌ No autenticado | Haz login de nuevo |
| 403 Forbidden | ❌ Sin permisos | Necesitas rol admin |
| 404 Not Found | ❌ No existe | Verifica la URL |
| 422 Validation Error | ❌ Datos inválidos | Revisa el formato JSON |

---

## 💡 Consejos Útiles

### ✅ Shortcuts de Swagger

- **Ctrl+Click** en un endpoint → Abre en nueva pestaña
- **Scroll hasta abajo** → Verás "Schemas" (modelos de datos)
- **Click en "curl"** → Copia el comando para terminal

### ✅ Copiar como Comando curl

En cada respuesta, puedes copiar el comando curl:

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/v1/topics' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbG...'
```

### ✅ Filtrar Resultados

Algunos endpoints aceptan query parameters:

```
GET /v1/exercises?topic_id=abc123&level_id=xyz789
```

---

## 🔄 Workflow Típico

```
1. Iniciar servidor
   ↓
2. Abrir http://127.0.0.1:8000/docs
   ↓
3. Login (POST /v1/auth/login)
   ↓
4. Copiar token
   ↓
5. Click "Authorize" y pegar token
   ↓
6. ¡Explorar todos los endpoints!
   ↓
   • Ver topics
   • Ver levels
   • Ver exercises
   • Ver usuarios
   • Crear nuevos datos
   • Actualizar datos
   • Eliminar datos
```

---

## 🎯 Próximos Pasos

Una vez que veas los datos, puedes:

1. **Crear más datos** usando los endpoints POST
2. **Actualizar datos** usando los endpoints PUT/PATCH
3. **Eliminar datos** usando los endpoints DELETE
4. **Exportar datos** copiando el JSON de la respuesta
5. **Importar datos** desde la app móvil usando estos mismos endpoints

---

## 📝 Recordatorio

**TODOS estos datos vienen de LocalStack DynamoDB:**

- 📂 Ubicación física: `localstack/localstack-data/`
- 🔄 Persisten aunque apagues la PC
- 🗑️ Se borran solo si ejecutas `docker-compose down -v`

¡Explora la API! 🚀
