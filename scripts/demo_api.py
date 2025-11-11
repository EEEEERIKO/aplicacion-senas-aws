"""
Script de demostración: Cómo acceder a los datos de LocalStack a través de la API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/v1"

print("=" * 70)
print("🔍 DEMOSTRACIÓN: Ver Datos de LocalStack a través de la API")
print("=" * 70)

# Paso 1: Login
print("\n📝 Paso 1: Hacer Login")
print("-" * 70)

login_data = {
    "email": "erikvalencia445@gmail.com",
    "password": "Erikvalencia1$"
}

print(f"POST {BASE_URL}/auth/login")
print(f"Body: {json.dumps(login_data, indent=2)}")

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        login_response = response.json()
        token = login_response["access_token"]
        user = login_response["user"]
        
        print(f"\n✅ Login exitoso!")
        print(f"   Usuario: {user['email']}")
        print(f"   Nombre: {user['name']}")
        print(f"   Rol: {user['role']}")
        print(f"   Token: {token[:50]}...")
        
        # Headers para peticiones autenticadas
        headers = {"Authorization": f"Bearer {token}"}
        
        # Paso 2: Ver Topics
        print("\n\n📚 Paso 2: Ver Topics (desde LocalStack)")
        print("-" * 70)
        print(f"GET {BASE_URL}/topics")
        
        topics_response = requests.get(f"{BASE_URL}/topics", headers=headers)
        if topics_response.status_code == 200:
            topics = topics_response.json()
            print(f"\n✅ {len(topics)} topics encontrados:")
            for i, topic in enumerate(topics, 1):
                print(f"\n   {i}. {topic['name']['pt_BR']} / {topic['name']['en_US']}")
                print(f"      ID: {topic['topic_id']}")
                print(f"      Descripción: {topic['description']['pt_BR']}")
        
        # Paso 3: Ver Levels
        print("\n\n📊 Paso 3: Ver Levels (desde LocalStack)")
        print("-" * 70)
        print(f"GET {BASE_URL}/levels")
        
        levels_response = requests.get(f"{BASE_URL}/levels", headers=headers)
        if levels_response.status_code == 200:
            levels = levels_response.json()
            print(f"\n✅ {len(levels)} levels encontrados:")
            for i, level in enumerate(levels, 1):
                print(f"\n   {i}. {level['name']['pt_BR']} / {level['name']['en_US']}")
                print(f"      Dificultad: {level['difficulty']}")
                print(f"      Score mínimo: {level['min_score']}")
        
        # Paso 4: Ver Exercises
        print("\n\n📝 Paso 4: Ver Exercises (desde LocalStack)")
        print("-" * 70)
        print(f"GET {BASE_URL}/exercises")
        
        exercises_response = requests.get(f"{BASE_URL}/exercises", headers=headers)
        if exercises_response.status_code == 200:
            exercises = exercises_response.json()
            print(f"\n✅ {len(exercises)} exercises encontrados:")
            for i, exercise in enumerate(exercises, 1):
                print(f"\n   {i}. {exercise['title']['pt_BR']} / {exercise['title']['en_US']}")
                print(f"      Tipo: {exercise['type']}")
                print(f"      Puntos: {exercise['points']}")
        
        # Paso 5: Ver Usuarios (solo admin)
        print("\n\n👥 Paso 5: Ver Usuarios (solo admin, desde LocalStack)")
        print("-" * 70)
        print(f"GET {BASE_URL}/auth/users")
        
        users_response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            print(f"\n✅ {len(users)} usuarios encontrados:")
            for i, u in enumerate(users, 1):
                print(f"\n   {i}. {u['email']}")
                print(f"      Nombre: {u['name']}")
                print(f"      Rol: {u['role']}")
                print(f"      ID: {u['user_id']}")
        
        # Resumen
        print("\n\n" + "=" * 70)
        print("✅ TODOS ESTOS DATOS VIENEN DE LOCALSTACK DYNAMODB")
        print("=" * 70)
        print("\n📍 Los datos están en: localstack/localstack-data/")
        print("🔄 Persisten aunque apagues la PC o reinicies LocalStack")
        print("\n💡 Puedes ver estos datos de 3 formas:")
        print("   1. API REST (como acabas de ver)")
        print("   2. Swagger UI: http://127.0.0.1:8000/docs")
        print("   3. Script directo: python scripts/check_data.py")
        
    else:
        print(f"\n❌ Error en login: {response.status_code}")
        print(response.json())

except requests.exceptions.ConnectionError:
    print("\n❌ Error: No se pudo conectar a la API")
    print("\n💡 Asegúrate de que el servidor esté corriendo:")
    print("   cd services/api")
    print("   .venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n")
