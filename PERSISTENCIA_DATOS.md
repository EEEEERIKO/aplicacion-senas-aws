# 💾 Persistencia de Datos - LocalStack

## ✅ Tus Datos SÍ Se Guardan

LocalStack está configurado con **persistencia de datos**, lo que significa que tus datos **NO se borran** cuando apagas el servidor o la computadora.

---

## 📂 Ubicación de los Datos

Los datos se guardan físicamente en tu disco duro en:

```
c:\ERIKO\UNASP\APLICACIÓN SEÑAS\aplicacion-senas-aws\localstack\localstack-data\
```

Esta carpeta contiene todos los datos de DynamoDB (usuarios, topics, levels, exercises, etc.)

---

## 🟢 Datos SE MANTIENEN Cuando:

### ✅ Apagas el Servidor FastAPI
```bash
# Puedes detener el servidor con Ctrl+C
# Los datos en DynamoDB se mantienen
```

### ✅ Detienes LocalStack
```bash
cd localstack
docker-compose stop
# Los datos están en localstack-data/
```

### ✅ Reinicias tu Computadora
```bash
# Al encender de nuevo:
docker start localstack-localstack-1
# Los datos siguen ahí
```

### ✅ Reinicias LocalStack
```bash
cd localstack
docker-compose restart
# Los datos se recargan automáticamente
```

---

## 🔴 Datos SE BORRAN Cuando:

### ❌ Ejecutas `docker-compose down -v`
```bash
cd localstack
docker-compose down -v  # ⚠️ El -v elimina volúmenes
```

### ❌ Borras la Carpeta de Datos
```bash
rm -rf localstack/localstack-data/  # ⚠️ Elimina todos los datos
```

### ❌ Ejecutas Comandos de Limpieza de Docker
```bash
docker volume prune -f  # ⚠️ Elimina volúmenes no usados
docker system prune -a --volumes  # ⚠️ Limpieza completa
```

---

## 🔄 Flujo de Trabajo Normal

### Día 1 - Primera Vez
```bash
# 1. Iniciar LocalStack
cd localstack
docker-compose up -d

# 2. Crear tablas y cargar datos
cd ..
python scripts/setup_dynamodb.py
python scripts/seed_data_direct.py

# 3. Iniciar API
cd services/api
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# ✅ Trabajas todo el día...
```

### Día 2 - Siguiente Día (después de reiniciar PC)
```bash
# 1. Solo verificar que LocalStack esté corriendo
docker ps  # Ver si está corriendo

# Si no está corriendo:
docker start localstack-localstack-1

# 2. Iniciar API (los datos ya están en DynamoDB)
cd services/api
.venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# ✅ Tus datos siguen ahí (admin, topics, levels, exercises)
```

---

## 🧪 Verificar que los Datos Están Guardados

### Opción 1: Con Python
```bash
python -c "
import boto3
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url='http://localhost:4566',
    region_name='us-east-1',
    aws_access_key_id='test',
    aws_secret_access_key='test'
)
table = dynamodb.Table('aplicacion-senas-content')
response = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'user'})
print(f'Usuarios: {len(response[\"Items\"])}')
"
```

### Opción 2: Verificar la Carpeta
```bash
ls -lh localstack/localstack-data/
# Verás archivos si hay datos guardados
```

### Opción 3: Probar Login en la API
1. Abre http://127.0.0.1:8000/docs
2. Intenta hacer login con `erikvalencia445@gmail.com`
3. Si funciona, los datos están ahí ✅

---

## 🗑️ Limpiar y Empezar de Cero

Si quieres **borrar todos los datos** y empezar de cero:

```bash
# 1. Detener LocalStack
cd localstack
docker-compose down

# 2. Eliminar datos
rm -rf localstack-data/

# 3. Reiniciar LocalStack
docker-compose up -d

# 4. Esperar 10-15 segundos

# 5. Crear tablas y cargar datos de nuevo
cd ..
python scripts/setup_dynamodb.py
python scripts/seed_data_direct.py
```

---

## 📊 Tamaño de los Datos

LocalStack es muy ligero. Tus datos actuales ocupan muy poco espacio:

```bash
# Ver tamaño de la carpeta de datos
du -sh localstack/localstack-data/
```

Con:
- 1 usuario admin
- 3 topics
- 4 levels  
- 2 exercises

Probablemente ocupa **menos de 10 MB** 📁

---

## ⚙️ Configuración de Persistencia

Esta es la configuración en `localstack/docker-compose.yml`:

```yaml
volumes:
  - ./localstack-data:/var/lib/localstack
```

Esto mapea la carpeta local `localstack-data/` al directorio interno de LocalStack donde guarda los datos.

---

## 🎯 Ventajas de la Persistencia

### ✅ Desarrollo Más Rápido
- No necesitas recargar datos cada vez que inicias
- Login del admin siempre funciona
- Topics, exercises, etc. siempre disponibles

### ✅ Trabajo Continuo
- Puedes apagar tu PC sin perder trabajo
- Los datos de prueba se mantienen
- No necesitas configurar nada adicional

### ✅ Simulación Realista
- Simula cómo funciona DynamoDB real en AWS
- Los datos persisten como en producción
- Puedes hacer backup de `localstack-data/`

---

## 🔐 Seguridad

⚠️ **IMPORTANTE**: La carpeta `localstack-data/` está en `.gitignore`, por lo que:

- ✅ NO se sube a GitHub
- ✅ Tus datos locales son privados
- ✅ Cada desarrollador tiene sus propios datos

---

## 📝 Resumen

| Acción | ¿Se Borran los Datos? |
|--------|----------------------|
| Cerrar servidor FastAPI | ❌ NO |
| Apagar computadora | ❌ NO |
| `docker-compose stop` | ❌ NO |
| `docker-compose restart` | ❌ NO |
| Reiniciar Docker Desktop | ❌ NO |
| `docker-compose down` (sin -v) | ❌ NO |
| `docker-compose down -v` | ✅ SÍ |
| Borrar `localstack-data/` | ✅ SÍ |

---

## 💡 Consejos

1. **Usa `docker-compose stop`** en lugar de `down` para mantener los datos
2. **Haz backup** de `localstack-data/` antes de cambios grandes
3. **Verifica los datos** con el script de verificación después de reiniciar
4. **No ejecutes** comandos de limpieza de Docker sin verificar primero

¡Tus datos están seguros! 🎉
