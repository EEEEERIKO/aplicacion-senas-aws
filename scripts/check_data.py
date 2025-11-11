"""
Script para verificar datos guardados en LocalStack DynamoDB
"""
import boto3

# DynamoDB configuration
DYNAMODB_ENDPOINT = "http://localhost:4566"
TABLE_NAME = "aplicacion-senas-content"
REGION = "us-east-1"

# Initialize DynamoDB client
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=DYNAMODB_ENDPOINT,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

table = dynamodb.Table(TABLE_NAME)

print("=" * 60)
print("📊 DATOS GUARDADOS EN LOCALSTACK DYNAMODB")
print("=" * 60)

try:
    # Usuarios
    users = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'user'})
    print(f'\n👥 Usuarios: {len(users["Items"])}')
    for user in users['Items']:
        print(f'   - {user["email"]} (rol: {user["role"]})')
    
    # Topics
    topics = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'topic'})
    print(f'\n📚 Topics: {len(topics["Items"])}')
    for topic in topics['Items']:
        print(f'   - {topic["name"]["pt_BR"]}')
    
    # Levels
    levels = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'level'})
    print(f'\n📊 Levels: {len(levels["Items"])}')
    for level in levels['Items']:
        print(f'   - {level["name"]["pt_BR"]} (dificultad: {level["difficulty"]})')
    
    # Exercises
    exercises = table.scan(FilterExpression='entity_type = :et', ExpressionAttributeValues={':et': 'exercise'})
    print(f'\n📝 Exercises: {len(exercises["Items"])}')
    for exercise in exercises['Items']:
        print(f'   - {exercise["title"]["pt_BR"]}')
    
    print("\n" + "=" * 60)
    print("✅ ESTOS DATOS PERSISTEN AUNQUE:")
    print("=" * 60)
    print("  ✓ Apagues el servidor FastAPI")
    print("  ✓ Reinicies tu computadora")
    print("  ✓ Detengas LocalStack con 'docker-compose stop'")
    print("  ✓ Reinicies LocalStack con 'docker-compose restart'")
    print("\n📂 Ubicación física: localstack/localstack-data/")
    print("\n⚠️  Solo se borran con:")
    print("  ✗ docker-compose down -v")
    print("  ✗ Borrar manualmente localstack-data/")
    
except Exception as e:
    print(f"\n❌ Error al verificar datos: {e}")
    print("\n💡 Asegúrate de que LocalStack esté corriendo:")
    print("   cd localstack && docker-compose up -d")
