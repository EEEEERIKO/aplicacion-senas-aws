"""
Direct DynamoDB seed script - bypasses API
Loads data directly into DynamoDB LocalStack
"""
import boto3
import hashlib
from decimal import Decimal
import uuid
from datetime import datetime
from passlib.context import CryptContext

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

# Password hashing - MUST match API exactly
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prehash_password(password: str) -> str:
    """
    Pre-hash password with SHA256 to support longer passwords.
    This is IDENTICAL to the API's implementation in app/core/auth.py
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def hash_password(password: str) -> str:
    """
    Hash password using SHA256 + bcrypt (EXACT same method as API).
    This MUST produce the same hash as app/core/auth.py
    """
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)

def create_admin_user():
    """Create admin user directly in DynamoDB"""
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Create admin user with erikvalencia445@gmail.com
    admin_user = {
        'PK': f'USER#{user_id}',
        'SK': f'PROFILE',
        'entity_type': 'user',
        'user_id': user_id,
        'email': 'erikvalencia445@gmail.com',  # Normalizado a minúsculas
        'password_hash': hash_password('Erikvalencia1$'),  # Nota: En producción usar bcrypt
        'name': 'Eriko',
        'role': 'admin',  # ROL ADMIN
        'language_preference': 'pt_BR',
        'created_at': now,
        'updated_at': now
    }
    
    print(f"✅ Creating admin user: {admin_user['email']}")
    table.put_item(Item=admin_user)
    return user_id

def create_topics():
    """Create topics"""
    topics = [
        {
            'topic_id': str(uuid.uuid4()),
            'name': {'pt_BR': 'Alfabeto', 'en_US': 'Alphabet'},
            'description': {'pt_BR': 'Aprenda as letras do alfabeto em Libras', 'en_US': 'Learn the alphabet letters in Sign Language'},
            'icon_url': 'https://example.com/icons/alphabet.png',
            'order_index': Decimal('1')
        },
        {
            'topic_id': str(uuid.uuid4()),
            'name': {'pt_BR': 'Cumprimentos', 'en_US': 'Greetings'},
            'description': {'pt_BR': 'Saudações e cumprimentos básicos', 'en_US': 'Basic greetings and salutations'},
            'icon_url': 'https://example.com/icons/greetings.png',
            'order_index': Decimal('2')
        },
        {
            'topic_id': str(uuid.uuid4()),
            'name': {'pt_BR': 'Números', 'en_US': 'Numbers'},
            'description': {'pt_BR': 'Números de 0 a 100', 'en_US': 'Numbers from 0 to 100'},
            'icon_url': 'https://example.com/icons/numbers.png',
            'order_index': Decimal('3')
        }
    ]
    
    print("\n📚 Creating topics...")
    for topic in topics:
        now = datetime.utcnow().isoformat()
        item = {
            'PK': f'TOPIC#{topic["topic_id"]}',
            'SK': 'METADATA',
            'entity_type': 'topic',
            **topic,
            'created_at': now,
            'updated_at': now
        }
        table.put_item(Item=item)
        print(f"  ✅ {topic['name']['pt_BR']}")
    
    return [t['topic_id'] for t in topics]

def create_levels():
    """Create difficulty levels"""
    levels = [
        {'level_id': str(uuid.uuid4()), 'name': {'pt_BR': 'Iniciante', 'en_US': 'Beginner'}, 'difficulty': Decimal('1'), 'min_score': Decimal('0')},
        {'level_id': str(uuid.uuid4()), 'name': {'pt_BR': 'Básico', 'en_US': 'Basic'}, 'difficulty': Decimal('2'), 'min_score': Decimal('100')},
        {'level_id': str(uuid.uuid4()), 'name': {'pt_BR': 'Intermediário', 'en_US': 'Intermediate'}, 'difficulty': Decimal('3'), 'min_score': Decimal('300')},
        {'level_id': str(uuid.uuid4()), 'name': {'pt_BR': 'Avançado', 'en_US': 'Advanced'}, 'difficulty': Decimal('4'), 'min_score': Decimal('600')}
    ]
    
    print("\n📊 Creating levels...")
    for level in levels:
        now = datetime.utcnow().isoformat()
        item = {
            'PK': f'LEVEL#{level["level_id"]}',
            'SK': 'METADATA',
            'entity_type': 'level',
            **level,
            'created_at': now,
            'updated_at': now
        }
        table.put_item(Item=item)
        print(f"  ✅ {level['name']['pt_BR']} (Difficulty: {level['difficulty']})")
    
    return [l['level_id'] for l in levels]

def create_exercises(topic_ids, level_ids):
    """Create sample exercises"""
    exercises = [
        # Alphabet topic exercises
        {
            'topic_id': topic_ids[0],
            'level_id': level_ids[0],
            'type': 'gesture_recognition',
            'title': {'pt_BR': 'Letra A', 'en_US': 'Letter A'},
            'description': {'pt_BR': 'Identifique a letra A', 'en_US': 'Identify letter A'},
            'video_url': 'https://example.com/videos/letter_a.mp4',
            'points': Decimal('10')
        },
        # Greetings topic exercises
        {
            'topic_id': topic_ids[1],
            'level_id': level_ids[0],
            'type': 'gesture_recognition',
            'title': {'pt_BR': 'Olá', 'en_US': 'Hello'},
            'description': {'pt_BR': 'Aprenda a dizer olá', 'en_US': 'Learn to say hello'},
            'video_url': 'https://example.com/videos/hello.mp4',
            'points': Decimal('15')
        }
    ]
    
    print("\n📝 Creating exercises...")
    for exercise in exercises:
        exercise_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        item = {
            'PK': f'EXERCISE#{exercise_id}',
            'SK': 'METADATA',
            'entity_type': 'exercise',
            'exercise_id': exercise_id,
            **exercise,
            'created_at': now,
            'updated_at': now
        }
        table.put_item(Item=item)
        print(f"  ✅ {exercise['title']['pt_BR']}")

def main():
    print("=" * 80)
    print("🌱 DIRECT DATABASE SEEDING (LocalStack DynamoDB)")
    print("=" * 80)
    
    try:
        # Create admin user
        print("\n👤 Creating admin user...")
        admin_id = create_admin_user()
        print(f"  ✅ Admin created with ID: {admin_id}")
        print("  📧 Email: erikvalencia445@gmail.com")
        print("  🔑 Password: Erikvalencia1$")
        print("  👑 Role: admin")
        
        # Create topics
        topic_ids = create_topics()
        
        # Create levels
        level_ids = create_levels()
        
        # Create exercises
        create_exercises(topic_ids, level_ids)
        
        print("\n" + "=" * 80)
        print("✅ SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\n📌 Next steps:")
        print("  1. Start the API server if not running:")
        print("     cd services/api && .venv/Scripts/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000")
        print("\n  2. Test the API at: http://127.0.0.1:8000/docs")
        print("\n  3. Login with:")
        print("     Email: erikvalencia445@gmail.com")
        print("     Password: Erikvalencia1$")
        print("\n✅ Password is properly hashed with SHA256 + bcrypt (production-ready)")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
