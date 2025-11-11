# 🚀 Inicio Rápido - Aplicación Señas Backend

## ✅ Estado Actual del Sistema

### Datos Cargados en LocalStack DynamoDB:
- ✅ **Usuario Admin**: erikvalencia445@gmail.com / Erikvalencia1$
- ✅ **3 Topics**: Alfabeto, Cumprimentos, Números
- ✅ **4 Levels**: Iniciante, Básico, Intermediário, Avançado
- ✅ **2 Exercises**: Letra A, Olá

---

## 📋 Pasos para Iniciar el Backend

### 1️⃣ Verificar LocalStack (DynamoDB)

```bash
# Verificar que LocalStack esté corriendo
docker ps

# Si no está corriendo, iniciarlo:
cd localstack
docker-compose up -d

# Esperar 10-15 segundos para que esté listo
```

### 2️⃣ Iniciar el Servidor FastAPI

```bash
# Desde la carpeta del proyecto
cd "services/api"

# Iniciar con uvicorn
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3️⃣ Abrir la Documentación de la API

Abre en tu navegador: **http://127.0.0.1:8000/docs**

---

## 🔑 Credenciales de Admin

```
Email: erikvalencia445@gmail.com
Password: Erikvalencia1$
Role: admin
```

---

## 🧪 Probar la API

### Opción 1: Usar Swagger UI (Recomendado)

1. Abre http://127.0.0.1:8000/docs
2. Expande **POST /v1/auth/login**
3. Click en "Try it out"
4. Ingresa las credenciales:
   ```json
   {
     "email": "erikvalencia445@gmail.com",
     "password": "Erikvalencia1$"
   }
   ```
5. Click "Execute"
6. Copia el `access_token` de la respuesta
7. Click en "Authorize" (botón verde arriba a la derecha)
8. Pega el token en el campo "Value"
9. ¡Ya puedes probar todos los endpoints protegidos!

### Opción 2: Usar curl

```bash
# Login y obtener token
curl -X POST http://127.0.0.1:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"erikvalencia445@gmail.com","password":"Erikvalencia1$"}'

# Usar el token para acceder a recursos protegidos
curl -X GET http://127.0.0.1:8000/v1/auth/me \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 📚 Endpoints Principales

### Autenticación
- `POST /v1/auth/register` - Registrar nuevo usuario
- `POST /v1/auth/login` - Iniciar sesión
- `GET /v1/auth/me` - Ver perfil actual
- `GET /v1/auth/users` - Listar usuarios (admin only)
- `PATCH /v1/auth/users/{user_id}/role` - Promover/degradar usuario (admin only)

### Contenido
- `GET /v1/languages` - Obtener idiomas disponibles
- `GET /v1/topics` - Listar topics
- `GET /v1/levels` - Listar niveles
- `GET /v1/exercises` - Listar ejercicios
- `GET /v1/progress` - Ver progreso del usuario
- `GET /v1/leaderboards` - Ver rankings

---

## 🔄 Reiniciar Todo desde Cero

Si necesitas limpiar y reiniciar todo:

```bash
# 1. Detener LocalStack
cd localstack
docker-compose down

# 2. Eliminar volúmenes (limpia datos)
docker volume prune -f

# 3. Reiniciar LocalStack
docker-compose up -d

# 4. Esperar 10-15 segundos

# 5. Crear tablas y cargar datos
cd ..
python scripts/setup_dynamodb.py
python scripts/seed_data_direct.py

# 6. Iniciar API
cd services/api
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🐛 Solución de Problemas

### Error: "Unknown table: aplicacion-senas-content"

**Solución:** Las tablas no están creadas. Ejecuta:
```bash
python scripts/setup_dynamodb.py
python scripts/seed_data_direct.py
```

### Error: "Connection refused" en port 4566

**Solución:** LocalStack no está corriendo. Ejecuta:
```bash
cd localstack
docker-compose up -d
```

### Error: "Incorrect email or password"

**Solución:** Verifica que los datos estén cargados:
```bash
python scripts/seed_data_direct.py
```

### El servidor se cierra al hacer peticiones

**Solución:** Usa `127.0.0.1` en lugar de `localhost`:
```
http://127.0.0.1:8000/docs
```

---

## 📊 Verificar Datos en DynamoDB

```bash
# Ver todas las tablas
python -c "import boto3; client = boto3.client('dynamodb', endpoint_url='http://localhost:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test'); print(client.list_tables()['TableNames'])"

# Ver usuarios
python -c "import boto3; dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566', region_name='us-east-1', aws_access_key_id='test', aws_secret_access_key='test'); table = dynamodb.Table('aplicacion-senas-content'); response = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'user'}); print(f'Usuarios: {len(response[\"Items\"])}')"
```

---

## 🎯 URLs Útiles

- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **API Docs (ReDoc)**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/healthz
- **Root Endpoint**: http://127.0.0.1:8000/
- **LocalStack Dashboard**: http://localhost:4566

---

## 📝 Notas Importantes

1. **Todos los datos están en LocalStack** - Si reinicias Docker, los datos se pierden (a menos que uses volúmenes persistentes)

2. **El password está hasheado con SHA256 + bcrypt** - Es seguro y sigue el mismo flujo que producción

3. **El servidor auto-recarga** - Con `--reload`, los cambios en el código se aplican automáticamente

4. **CORS está habilitado** - Puedes hacer peticiones desde cualquier origen (configura para producción)

5. **Los tokens expiran en 30 minutos** - Tendrás que volver a hacer login después

---

## ✅ Checklist de Inicio

- [ ] LocalStack corriendo (`docker ps`)
- [ ] Tablas creadas (`python scripts/setup_dynamodb.py`)
- [ ] Datos cargados (`python scripts/seed_data_direct.py`)
- [ ] API corriendo en http://127.0.0.1:8000
- [ ] Swagger abierto en http://127.0.0.1:8000/docs
- [ ] Login exitoso con erikvalencia445@gmail.com

¡Todo listo para desarrollar! 🚀
