#!/usr/bin/env python3
"""
Script para crear las tablas de DynamoDB en LocalStack
y cargar los datos iniciales
"""
import boto3
from decimal import Decimal

# Configuración de LocalStack
ENDPOINT_URL = "http://localhost:4566"
REGION = "us-east-1"
TABLE_NAME = "aplicacion-senas-content"

# Cliente de DynamoDB
dynamodb = boto3.client(
    'dynamodb',
    endpoint_url=ENDPOINT_URL,
    region_name=REGION,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

def create_table():
    """Crear la tabla principal de DynamoDB"""
    print(f"Creando tabla {TABLE_NAME}...")
    
    try:
        dynamodb.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'entity_type', 'AttributeType': 'S'},
                {'AttributeName': 'created_at', 'AttributeType': 'S'},
                {'AttributeName': 'topic_id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
            ],
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'entity_type-created_at-index',
                    'KeySchema': [
                        {'AttributeName': 'entity_type', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'topic_id-SK-index',
                    'KeySchema': [
                        {'AttributeName': 'topic_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'SK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("✅ Tabla creada exitosamente")
        return True
    except dynamodb.exceptions.ResourceInUseException:
        print("⚠️  La tabla ya existe")
        return False
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
        return False

def verify_table():
    """Verificar que la tabla existe"""
    try:
        response = dynamodb.describe_table(TableName=TABLE_NAME)
        status = response['Table']['TableStatus']
        print(f"✅ Tabla {TABLE_NAME} - Estado: {status}")
        return True
    except Exception as e:
        print(f"❌ Error al verificar la tabla: {e}")
        return False

def main():
    print("=" * 50)
    print("Setup de DynamoDB en LocalStack")
    print("=" * 50)
    print()
    
    # Crear tabla
    create_table()
    print()
    
    # Verificar tabla
    verify_table()
    print()
    
    print("=" * 50)
    print("✅ Setup completado!")
    print("=" * 50)
    print()
    print("Ahora puedes ejecutar el script de seed:")
    print("  python scripts/seed_database.py")
    print()

if __name__ == "__main__":
    main()
