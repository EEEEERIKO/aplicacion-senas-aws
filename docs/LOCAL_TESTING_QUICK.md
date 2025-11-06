# 🚀 Local Testing Guide - Quick Start

Esta guía te ayudará a probar el backend con **DynamoDB, Lambda y API Gateway** en tu máquina local usando **LocalStack**.

---

## 📋 Prerequisitos

Antes de empezar, asegúrate de tener instalado:

- ✅ **Docker Desktop** (corriendo)
- ✅ **AWS CLI** ([Instalar](https://aws.amazon.com/cli/))
- ✅ **Python 3.9+**
- ✅ **Terraform** (opcional, solo para deploy a AWS)

### Instalar AWS CLI

```bash
# Windows (con Chocolatey)
choco install awscli

# O descargar desde: https://aws.amazon.com/cli/
```

---

## 🏃 Opción 1: Setup Automático (Recomendado)

Ejecuta **un solo script** que configura todo:

```bash
cd scripts
bash setup_local.sh
```

Este script hará:
1. ✅ Iniciar LocalStack (Docker)
2. ✅ Crear tabla DynamoDB con GSIs
3. ✅ Crear bucket S3
4. ✅ Insertar datos de prueba
5. ✅ Empaquetar Lambda
6. ✅ Desplegar Lambda a LocalStack
7. ✅ Crear API Gateway
8. ✅ Ejecutar smoke tests

**Duración:** ~2 minutos

Al finalizar verás:

```
========================================
Setup Complete!
========================================

API Gateway Endpoint: http://localhost:4566/restapis/abc123/test/_user_request_
DynamoDB Endpoint: http://localhost:4566
S3 Endpoint: http://localhost:4566
```

---

## 🔧 Opción 2: Setup Manual (Paso a Paso)

### Paso 1: Iniciar LocalStack

```bash
cd localstack
docker-compose up -d
```

Verifica que esté corriendo:

```bash
curl http://localhost:4566/_localstack/health
```

### Paso 2: Crear Tabla DynamoDB

```bash
aws dynamodb create-table \
    --table-name aplicacion-senas-content \
    --attribute-definitions \
        AttributeName=PK,AttributeType=S \
        AttributeName=SK,AttributeType=S \
        AttributeName=entity_type,AttributeType=S \
        AttributeName=created_at,AttributeType=S \
        AttributeName=topic_id,AttributeType=S \
    --key-schema \
        AttributeName=PK,KeyType=HASH \
        AttributeName=SK,KeyType=RANGE \
    --global-secondary-indexes \
        '[{"IndexName":"entity_type-created_at-index","KeySchema":[{"AttributeName":"entity_type","KeyType":"HASH"},{"AttributeName":"created_at","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}},{"IndexName":"topic_id-SK-index","KeySchema":[{"AttributeName":"topic_id","KeyType":"HASH"},{"AttributeName":"SK","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]' \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:4566 \
    --region us-east-1
```

### Paso 3: Insertar Datos de Prueba

```bash
cd scripts
export DYNAMO_ENDPOINT_URL=http://localhost:4566
export DYNAMO_TABLE=aplicacion-senas-content
bash seed_dynamo_local.sh
```

### Paso 4: Probar con FastAPI Directo (Sin Lambda)

```bash
cd services/api

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.local .env

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

Abre tu navegador en: http://localhost:8000/docs

---

## 🧪 Probar los Endpoints

### Con FastAPI directo (puerto 8000)

```bash
# Health check
curl http://localhost:8000/healthz

# Root
curl http://localhost:8000/

# Docs interactivos
open http://localhost:8000/docs
```

### Con API Gateway en LocalStack (puerto 4566)

```bash
# Obtener API ID
API_ID=$(aws apigatewayv2 get-apis \
    --endpoint-url http://localhost:4566 \
    --query 'Items[0].ApiId' \
    --output text)

# Probar endpoint
curl http://localhost:4566/restapis/${API_ID}/test/_user_request_/healthz
```

---

## 🔍 Ver Datos en DynamoDB

```bash
# Ver todas las tablas
aws dynamodb list-tables --endpoint-url http://localhost:4566

# Scan completo de la tabla
aws dynamodb scan \
    --table-name aplicacion-senas-content \
    --endpoint-url http://localhost:4566 \
    --region us-east-1

# Query por PK
aws dynamodb query \
    --table-name aplicacion-senas-content \
    --key-condition-expression "PK = :pk" \
    --expression-attribute-values '{":pk":{"S":"LANG#pt_BR"}}' \
    --endpoint-url http://localhost:4566
```

---

## 📦 Empaquetar Lambda

```bash
cd services/api
bash package_lambda.sh
```

Esto crea `lambda_deployment.zip` con todas las dependencias.

---

## 🛑 Detener LocalStack

```bash
cd localstack
docker-compose down
```

O eliminar todo (incluyendo datos):

```bash
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Docker no está corriendo

```
Error: Cannot connect to Docker daemon
```

**Solución:** Inicia Docker Desktop y espera a que esté listo.

### Puerto 4566 ya en uso

```
Error: Port 4566 is already in use
```

**Solución:**

```bash
# Ver qué está usando el puerto
netstat -ano | findstr :4566

# Detener LocalStack existente
docker ps
docker stop <container_id>
```

### AWS CLI no encontrado

```
Error: aws: command not found
```

**Solución:** Instala AWS CLI:

```bash
# Windows
choco install awscli

# O descarga desde: https://aws.amazon.com/cli/
```

### Error al crear tabla

```
ResourceInUseException: Table already exists
```

**Solución:** La tabla ya existe, puedes ignorar el error o eliminarla:

```bash
aws dynamodb delete-table \
    --table-name aplicacion-senas-content \
    --endpoint-url http://localhost:4566
```

---

## 📊 Siguiente Paso: Implementar Routers

Ahora que tienes el ambiente local funcionando, puedes:

1. **Crear routers de DynamoDB** en `services/api/app/api/v1/dynamo.py`
2. **Implementar CRUD de topics, levels, exercises**
3. **Agregar autenticación JWT**
4. **Conectar con el frontend**

Ver: [`docs/DATABASE_DESIGN.md`](../docs/DATABASE_DESIGN.md) para el diseño completo.

---

## 🎯 Comandos Útiles

```bash
# Ver logs de LocalStack
docker-compose -f localstack/docker-compose.yml logs -f

# Reiniciar LocalStack
cd localstack && docker-compose restart

# Ver todas las APIs en LocalStack
aws apigatewayv2 get-apis --endpoint-url http://localhost:4566

# Invocar Lambda directamente
aws lambda invoke \
    --function-name aplicacion-senas-api \
    --payload '{"httpMethod":"GET","path":"/healthz"}' \
    --endpoint-url http://localhost:4566 \
    response.json
```

---

## ✅ Checklist de Configuración

- [ ] Docker Desktop instalado y corriendo
- [ ] AWS CLI instalado
- [ ] LocalStack iniciado (`docker-compose up`)
- [ ] Tabla DynamoDB creada
- [ ] Datos de prueba insertados
- [ ] FastAPI corriendo en puerto 8000
- [ ] Endpoints `/healthz` y `/` responden
- [ ] DynamoDB query funciona

---

**¿Todo listo?** 🎉 Ahora puedes empezar a desarrollar tus APIs!
