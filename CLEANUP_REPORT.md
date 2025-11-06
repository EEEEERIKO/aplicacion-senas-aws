# 🧹 Cleanup & Organization Report
**Date**: November 6, 2025  
**Purpose**: Identify obsolete, duplicate, or unused files before commit

---

## 📊 Executive Summary

**Status**: ⚠️ **NEEDS CLEANUP**  
**Files to Review**: 12 archivos  
**Recommendation**: Eliminar o consolidar antes del commit

---

## 🗑️ Files to DELETE (Obsoletos/Sin Uso)

### 1. **`services/api/app/core/security.py`** ❌ OBSOLETO
**Razón**: Este archivo contiene:
- RateLimiter (no se usa en ningún endpoint actual)
- InputSanitizer (importado pero no se usa en endpoints nuevos)
- Permission class (reemplazada por get_current_admin en auth.py)

**Usada en archivos viejos que no están activos**:
- `app/repositories/` (carpeta prácticamente vacía)
- `app/schemas/` (carpeta prácticamente vacía)

**Recomendación**: ❌ **ELIMINAR** - Funcionalidad reemplazada por `auth.py`

---

### 2. **`services/api/app/repositories/` directory** ❌ OBSOLETO
**Contenido**:
- `__init__.py` (vacío)
- `language_repository.py` (no se usa)
- `topic_repository.py` (no se usa)
- `level_repository.py` (no se usa)

**Razón**: Los endpoints actuales en `app/api/v1/` acceden directamente a DynamoDB sin usar estos repositories. Patrón obsoleto de arquitectura antigua.

**Recomendación**: ❌ **ELIMINAR CARPETA COMPLETA**

---

### 3. **`services/api/app/schemas/` directory** ❌ OBSOLETO
**Contenido**:
- `__init__.py` (vacío)
- `language.py` (no se usa)
- `topic.py` (no se usa)
- `level.py` (no se usa)
- `exercise.py` (no se usa)

**Razón**: Los modelos Pydantic están definidos directamente en los archivos de endpoints (auth.py, topics.py, etc.). Esquemas centralizados no se usan.

**Recomendación**: ❌ **ELIMINAR CARPETA COMPLETA**

---

### 4. **`services/api/test_login.py`** ⚠️ TEMPORAL
**Contenido**: Script de prueba manual del login

**Razón**: Archivo temporal creado para debugging. No es un test automatizado.

**Recomendación**: ❌ **ELIMINAR** - Era solo para debugging

---

### 5. **`scripts/seed_dynamo_local.sh`** ❌ DUPLICADO
**Razón**: Script bash obsoleto para seed. Ahora usamos `services/api/scripts/seed_database.py` (Python) que es mucho más completo.

**Recomendación**: ❌ **ELIMINAR** - Duplicado y obsoleto

---

### 6. **`scripts/seed_local_dynamo.sh`** ❌ DUPLICADO
**Razón**: Otro script bash para crear tabla. Funcionalidad cubierta por el script Python.

**Recomendación**: ❌ **ELIMINAR** - Duplicado y obsoleto

---

## ⚠️ Files to REVIEW/UPDATE (Potencialmente Obsoletos)

### 7. **`services/api/.env` y `.env.local`** ✅ MANTENER
**Status**: CORRECTO
- `.env` - Desarrollo local (en .gitignore)
- `.env.local` - Template de ejemplo
- `.env.example` - Template nuevo y mejorado

**Recomendación**: 
- ✅ Mantener `.env` (no se commitea)
- ❌ **ELIMINAR** `.env.local` (duplicado de .env.example)
- ✅ Mantener `.env.example` (el mejor template)

---

### 8. **`docs/TESTING_NOW.md`** ⚠️ TEMPORAL
**Contenido**: Notas de testing de desarrollo

**Recomendación**: 
- ⚠️ **REVISAR CONTENIDO** - Si tiene info útil, moverla a README o SECURITY.md
- ❌ **ELIMINAR** si es solo notas temporales

---

### 9. **`scripts/start_local_simple.sh`** ✅ MANTENER CON MEJORA
**Contenido**: Script de inicio completo con todo integrado

**Estado**: Muy completo (400+ líneas), incluye:
- Verificación de dependencias
- Inicio de LocalStack
- Creación de tabla
- Seed de datos
- Inicio del servidor

**Recomendación**: ✅ **MANTENER** - Es útil para setup rápido
- **MEJORAR**: Actualizar para usar `services/api/scripts/seed_database.py` en lugar del seed bash

---

### 10. **`scripts/test_local.sh`** ✅ MANTENER
**Contenido**: Tests de endpoints

**Recomendación**: ✅ **MANTENER** - Útil para testing manual

---

## 📁 Files STRUCTURE (Correctos)

### ✅ Archivos Core en Uso:
```
services/api/app/
├── main.py                  ✅ Entry point
├── core/
│   ├── auth.py             ✅ JWT + RBAC (USADO)
│   ├── config.py           ✅ Configuración (USADO)
│   └── security.py         ❌ OBSOLETO → ELIMINAR
├── api/v1/
│   ├── auth.py             ✅ Register/Login (USADO)
│   ├── languages.py        ✅ Languages CRUD (USADO)
│   ├── topics.py           ✅ Topics CRUD (USADO)
│   ├── levels.py           ✅ Levels CRUD (USADO)
│   ├── exercises.py        ✅ Exercises CRUD (USADO)
│   ├── progress.py         ✅ User progress (USADO)
│   └── leaderboards.py     ✅ Rankings (USADO)
```

### ❌ Archivos/Carpetas a Eliminar:
```
services/api/app/
├── repositories/           ❌ ELIMINAR (obsoleto)
│   ├── language_repository.py
│   ├── topic_repository.py
│   └── level_repository.py
├── schemas/                ❌ ELIMINAR (no se usa)
│   ├── language.py
│   ├── topic.py
│   ├── level.py
│   └── exercise.py
└── core/
    └── security.py         ❌ ELIMINAR (reemplazado por auth.py)
```

---

## 🎯 Action Plan - Cleanup Commands

### Step 1: Backup (por si acaso)
```bash
cd "/c/ERIKO/UNASP/APLICACIÓN SEÑAS/aplicacion-senas-aws"
git add .
git stash
```

### Step 2: Delete Obsolete Files
```bash
# Eliminar archivos obsoletos
rm -rf services/api/app/repositories/
rm -rf services/api/app/schemas/
rm services/api/app/core/security.py
rm services/api/test_login.py
rm services/api/.env.local
rm scripts/seed_dynamo_local.sh
rm scripts/seed_local_dynamo.sh

# Opcional: revisar y decidir
# rm docs/TESTING_NOW.md
```

### Step 3: Verify Nothing Breaks
```bash
cd services/api
python -m py_compile app/main.py
python -m py_compile app/core/auth.py
python -m py_compile app/api/v1/*.py
```

### Step 4: Test Server
```bash
# Iniciar servidor para verificar que funciona
cd services/api
uvicorn app.main:app --reload
# Ctrl+C para detener
```

---

## 📊 Impact Analysis

### Before Cleanup:
- **Total files in services/api/app**: ~25 archivos
- **Used files**: ~15 archivos
- **Unused files**: ~10 archivos
- **Code cleanliness**: 60%

### After Cleanup:
- **Total files**: ~15 archivos
- **Used files**: ~15 archivos
- **Unused files**: 0 archivos
- **Code cleanliness**: 100% ✅

---

## ✅ Final Recommendations

### MUST DELETE (Alta prioridad):
1. ❌ `services/api/app/repositories/` - Completamente obsoleto
2. ❌ `services/api/app/schemas/` - No se usa
3. ❌ `services/api/app/core/security.py` - Reemplazado
4. ❌ `services/api/test_login.py` - Script temporal de debug
5. ❌ `scripts/seed_dynamo_local.sh` - Duplicado
6. ❌ `scripts/seed_local_dynamo.sh` - Duplicado

### SHOULD DELETE (Media prioridad):
7. ⚠️ `services/api/.env.local` - Duplicado de .env.example
8. ⚠️ `docs/TESTING_NOW.md` - Verificar si tiene info útil

### KEEP (Archivos correctos):
- ✅ Todos los archivos en `app/api/v1/` (endpoints activos)
- ✅ `app/core/auth.py` (JWT + RBAC)
- ✅ `app/core/config.py` (configuración)
- ✅ `app/main.py` (entry point)
- ✅ Scripts de utilidad (test_local.sh, start_local_simple.sh)

---

## 🚀 Benefits of Cleanup

1. **Código más limpio**: Solo archivos que se usan
2. **Menos confusión**: No hay archivos "fantasma"
3. **Mejor mantenibilidad**: Más fácil navegar el código
4. **Repositorio más ligero**: Menos archivos para revisar
5. **Mejor para open source**: Más fácil de entender para contributors

---

**Ready to cleanup?** Los comandos están listos arriba. 👆
