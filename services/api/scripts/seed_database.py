"""
Script to populate the database with initial data for the sign language learning app
Includes: Topics, Levels, Exercises with translations in pt_BR and en_US
"""
import requests
import json
import time
import os
from typing import Dict, List

# API Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/v1")
ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "admin@aplicacion-senas.com")
# ⚠️ SECURITY: Use environment variable for password in production!
ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "AdminSecure2024!")
ADMIN_NAME = os.getenv("INITIAL_ADMIN_NAME", "Sistema Administrador")

# Global variable to store auth token
AUTH_TOKEN = None

def register_admin() -> str:
    """Register admin user and return JWT token"""
    print("\n📝 Registering admin user...")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "name": ADMIN_NAME,
            "language_preference": "pt_BR",
            "role": "admin"
        }
    )
    
    # Check for success (200 or 201)
    if response.status_code in [200, 201]:
        token = response.json()["access_token"]
        user_id = response.json()["user"]["user_id"]
        print(f"✓ Admin registered successfully (ID: {user_id})")
        return token
    elif response.status_code == 400 and "already exists" in response.text.lower():
        # Try to login instead
        print("  Admin already exists, logging in...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ Admin logged in successfully")
            return token
    
    raise Exception(f"Failed to register/login admin (status {response.status_code}): {response.text}")

def get_auth_headers() -> Dict[str, str]:
    """Get authorization headers with JWT token"""
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def create_topic(slug: str, default_title: str, order: int, translations: Dict) -> str:
    """Create a topic and return its ID"""
    print(f"\n📚 Creating topic: {default_title}...")
    
    response = requests.post(
        f"{BASE_URL}/topics",
        headers=get_auth_headers(),
        json={
            "slug": slug,
            "default_title": default_title,
            "order": order,
            "is_published": True,
            "translations": translations
        }
    )
    
    if response.status_code in [200, 201]:
        topic_id = response.json()["topic_id"]
        print(f"✓ Topic created: {topic_id}")
        return topic_id
    else:
        raise Exception(f"Failed to create topic (status {response.status_code}): {response.text}")

def create_level(topic_id: str, slug: str, position: int, difficulty: int, 
                 metadata: Dict, translations: Dict) -> str:
    """Create a level and return its ID"""
    print(f"  📊 Creating level {position}...")
    
    response = requests.post(
        f"{BASE_URL}/levels",
        headers=get_auth_headers(),
        json={
            "topic_id": topic_id,
            "slug": slug,
            "position": position,
            "difficulty": difficulty,
            "is_published": True,
            "metadata": metadata,
            "translations": translations
        }
    )
    
    if response.status_code in [200, 201]:
        level_id = response.json()["level_id"]
        print(f"  ✓ Level created: {level_id}")
        return level_id
    else:
        raise Exception(f"Failed to create level (status {response.status_code}): {response.text}")

def create_exercise(level_id: str, exercise_type: str, position: int,
                   config: Dict, answer_schema: Dict, translations: Dict) -> str:
    """Create an exercise and return its ID"""
    print(f"    ✏️ Creating exercise {position} ({exercise_type})...")
    
    response = requests.post(
        f"{BASE_URL}/exercises",
        headers=get_auth_headers(),
        json={
            "level_id": level_id,
            "exercise_type": exercise_type,
            "position": position,
            "config": config,
            "answer_schema": answer_schema,
            "translations": translations
        }
    )
    
    if response.status_code in [200, 201]:
        exercise_id = response.json()["exercise_id"]
        print(f"    ✓ Exercise created: {exercise_id}")
        return exercise_id
    else:
        raise Exception(f"Failed to create exercise (status {response.status_code}): {response.text}")

# ==================== DATA DEFINITIONS ====================

def seed_alphabet_topic():
    """Seed the Alphabet topic with levels and exercises"""
    topic_id = create_topic(
        slug="alphabet",
        default_title="Alphabet",
        order=1,
        translations={
            "pt_BR": {
                "title": "Alfabeto",
                "description": "Aprenda o alfabeto completo em LIBRAS (Língua Brasileira de Sinais)"
            },
            "en_US": {
                "title": "Alphabet",
                "description": "Learn the complete alphabet in Brazilian Sign Language (LIBRAS)"
            }
        }
    )
    
    # Level 1: Letters A-E
    level1_id = create_level(
        topic_id=topic_id,
        slug="alphabet-letters-a-e",
        position=1,
        difficulty=1,
        metadata={
            "estimated_time_minutes": 10,
            "min_score_to_pass": 70,
            "max_attempts": 3
        },
        translations={
            "pt_BR": {
                "title": "Letras A-E",
                "description": "Aprenda as cinco primeiras letras do alfabeto",
                "hint": "Observe a posição dos dedos e o movimento da mão"
            },
            "en_US": {
                "title": "Letters A-E",
                "description": "Learn the first five letters of the alphabet",
                "hint": "Pay attention to finger position and hand movement"
            }
        }
    )
    
    # Exercise 1: MCQ for letter A
    create_exercise(
        level_id=level1_id,
        exercise_type="MCQ",
        position=1,
        config={
            "time_limit": 30,
            "choices_count": 4,
            "scoring_rules": {"correct": 20, "incorrect": 0}
        },
        answer_schema={"correct_answer": "A"},
        translations={
            "pt_BR": {
                "prompt_text": "Qual letra está sendo representada neste sinal?",
                "choice_texts": ["A", "B", "E", "O"],
                "feedback_text": {
                    "correct": "Muito bem! Esta é a letra A.",
                    "incorrect": "Não foi dessa vez. A letra A é feita com o punho fechado."
                }
            },
            "en_US": {
                "prompt_text": "Which letter is being represented in this sign?",
                "choice_texts": ["A", "B", "E", "O"],
                "feedback_text": {
                    "correct": "Great job! This is the letter A.",
                    "incorrect": "Not quite. The letter A is made with a closed fist."
                }
            }
        }
    )
    
    # Exercise 2: Camera exercise for letter B
    create_exercise(
        level_id=level1_id,
        exercise_type="CAMERA_PRODUCE",
        position=2,
        config={
            "time_limit": 45,
            "required_confidence": 0.8,
            "model_version": "v1.0",
            "scoring_rules": {"high_confidence": 25, "medium_confidence": 15, "low_confidence": 5}
        },
        answer_schema={"target_sign": "B"},
        translations={
            "pt_BR": {
                "prompt_text": "Faça o sinal da letra B com sua mão",
                "feedback_text": {
                    "correct": "Excelente! Você fez o sinal corretamente.",
                    "incorrect": "Tente novamente. Mantenha os dedos unidos e esticados para cima."
                }
            },
            "en_US": {
                "prompt_text": "Make the sign for letter B with your hand",
                "feedback_text": {
                    "correct": "Excellent! You made the sign correctly.",
                    "incorrect": "Try again. Keep your fingers together and stretched upward."
                }
            }
        }
    )
    
    # Exercise 3: Copy practice for letter C
    create_exercise(
        level_id=level1_id,
        exercise_type="COPY_PRACTICE",
        position=3,
        config={
            "time_limit": 60,
            "scoring_rules": {"completed": 15}
        },
        answer_schema={"target_sign": "C"},
        translations={
            "pt_BR": {
                "prompt_text": "Observe e copie o sinal da letra C",
                "feedback_text": {
                    "correct": "Ótimo trabalho praticando!",
                    "incorrect": "Continue praticando!"
                }
            },
            "en_US": {
                "prompt_text": "Watch and copy the sign for letter C",
                "feedback_text": {
                    "correct": "Great job practicing!",
                    "incorrect": "Keep practicing!"
                }
            }
        }
    )
    
    # Level 2: Letters F-J
    level2_id = create_level(
        topic_id=topic_id,
        slug="alphabet-letters-f-j",
        position=2,
        difficulty=1,
        metadata={
            "estimated_time_minutes": 12,
            "min_score_to_pass": 75,
            "max_attempts": 3
        },
        translations={
            "pt_BR": {
                "title": "Letras F-J",
                "description": "Continue aprendendo mais letras do alfabeto",
                "hint": "Preste atenção nos detalhes de cada sinal"
            },
            "en_US": {
                "title": "Letters F-J",
                "description": "Continue learning more letters of the alphabet",
                "hint": "Pay attention to the details of each sign"
            }
        }
    )
    
    # Add 3 exercises for level 2
    for i, letter in enumerate(["F", "G", "H"], 1):
        create_exercise(
            level_id=level2_id,
            exercise_type="MCQ" if i == 1 else "CAMERA_PRODUCE",
            position=i,
            config={
                "time_limit": 35,
                "choices_count": 4 if i == 1 else None,
                "required_confidence": 0.8 if i > 1 else None,
                "model_version": "v1.0" if i > 1 else None,
                "scoring_rules": {"correct": 20} if i == 1 else {"high_confidence": 25}
            },
            answer_schema={"correct_answer": letter} if i == 1 else {"target_sign": letter},
            translations={
                "pt_BR": {
                    "prompt_text": f"Qual letra está sendo representada?" if i == 1 else f"Faça o sinal da letra {letter}",
                    "choice_texts": [letter, "A", "E", "I"] if i == 1 else None,
                    "feedback_text": {
                        "correct": f"Correto! Esta é a letra {letter}.",
                        "incorrect": f"Tente novamente a letra {letter}."
                    }
                },
                "en_US": {
                    "prompt_text": f"Which letter is being shown?" if i == 1 else f"Make the sign for letter {letter}",
                    "choice_texts": [letter, "A", "E", "I"] if i == 1 else None,
                    "feedback_text": {
                        "correct": f"Correct! This is letter {letter}.",
                        "incorrect": f"Try again for letter {letter}."
                    }
                }
            }
        )
    
    return topic_id

def seed_greetings_topic():
    """Seed the Greetings topic"""
    topic_id = create_topic(
        slug="greetings",
        default_title="Greetings",
        order=2,
        translations={
            "pt_BR": {
                "title": "Saudações",
                "description": "Aprenda saudações básicas em LIBRAS"
            },
            "en_US": {
                "title": "Greetings",
                "description": "Learn basic greetings in Brazilian Sign Language"
            }
        }
    )
    
    # Level 1: Basic greetings
    level1_id = create_level(
        topic_id=topic_id,
        slug="basic-greetings",
        position=1,
        difficulty=1,
        metadata={
            "estimated_time_minutes": 15,
            "min_score_to_pass": 70,
            "max_attempts": 3
        },
        translations={
            "pt_BR": {
                "title": "Saudações Básicas",
                "description": "Olá, tchau, bom dia, boa tarde",
                "hint": "Observe o movimento completo do sinal"
            },
            "en_US": {
                "title": "Basic Greetings",
                "description": "Hello, goodbye, good morning, good afternoon",
                "hint": "Watch the complete movement of the sign"
            }
        }
    )
    
    # Exercise: Hello
    create_exercise(
        level_id=level1_id,
        exercise_type="CAMERA_PRODUCE",
        position=1,
        config={
            "time_limit": 40,
            "required_confidence": 0.75,
            "model_version": "v1.0",
            "scoring_rules": {"high_confidence": 30}
        },
        answer_schema={"target_sign": "HELLO"},
        translations={
            "pt_BR": {
                "prompt_text": "Faça o sinal de 'Olá'",
                "feedback_text": {
                    "correct": "Perfeito! Você cumprimentou corretamente.",
                    "incorrect": "Tente fazer um movimento de aceno com a mão."
                }
            },
            "en_US": {
                "prompt_text": "Make the sign for 'Hello'",
                "feedback_text": {
                    "correct": "Perfect! You greeted correctly.",
                    "incorrect": "Try making a waving motion with your hand."
                }
            }
        }
    )
    
    return topic_id

def seed_numbers_topic():
    """Seed the Numbers topic"""
    topic_id = create_topic(
        slug="numbers",
        default_title="Numbers",
        order=3,
        translations={
            "pt_BR": {
                "title": "Números",
                "description": "Aprenda a contar em LIBRAS"
            },
            "en_US": {
                "title": "Numbers",
                "description": "Learn to count in Brazilian Sign Language"
            }
        }
    )
    
    # Level 1: Numbers 1-10
    level1_id = create_level(
        topic_id=topic_id,
        slug="numbers-1-10",
        position=1,
        difficulty=1,
        metadata={
            "estimated_time_minutes": 20,
            "min_score_to_pass": 80,
            "max_attempts": 5
        },
        translations={
            "pt_BR": {
                "title": "Números 1-10",
                "description": "Aprenda os números de 1 a 10",
                "hint": "Cada número tem uma configuração específica de dedos"
            },
            "en_US": {
                "title": "Numbers 1-10",
                "description": "Learn numbers 1 to 10",
                "hint": "Each number has a specific finger configuration"
            }
        }
    )
    
    # Add exercises for numbers 1-5
    for i in range(1, 6):
        create_exercise(
            level_id=level1_id,
            exercise_type="MCQ" if i % 2 == 1 else "CAMERA_PRODUCE",
            position=i,
            config={
                "time_limit": 30,
                "choices_count": 4 if i % 2 == 1 else None,
                "required_confidence": 0.85 if i % 2 == 0 else None,
                "model_version": "v1.0" if i % 2 == 0 else None,
                "scoring_rules": {"correct": 20}
            },
            answer_schema={"correct_answer": str(i)} if i % 2 == 1 else {"target_sign": str(i)},
            translations={
                "pt_BR": {
                    "prompt_text": f"Que número é este?" if i % 2 == 1 else f"Faça o sinal do número {i}",
                    "choice_texts": [str(i), str(i+1), str(i+2), str(i-1 if i > 1 else 10)] if i % 2 == 1 else None,
                    "feedback_text": {
                        "correct": f"Correto! Este é o número {i}.",
                        "incorrect": f"Tente novamente o número {i}."
                    }
                },
                "en_US": {
                    "prompt_text": f"What number is this?" if i % 2 == 1 else f"Make the sign for number {i}",
                    "choice_texts": [str(i), str(i+1), str(i+2), str(i-1 if i > 1 else 10)] if i % 2 == 1 else None,
                    "feedback_text": {
                        "correct": f"Correct! This is number {i}.",
                        "incorrect": f"Try again for number {i}."
                    }
                }
            }
        )
    
    return topic_id

def main():
    """Main function to seed all data"""
    global AUTH_TOKEN
    
    print("="*60)
    print("🌱 DATABASE SEEDING SCRIPT")
    print("="*60)
    
    try:
        # Step 1: Register admin and get token
        AUTH_TOKEN = register_admin()
        
        # Step 2: Seed topics
        print("\n" + "="*60)
        print("📚 SEEDING TOPICS")
        print("="*60)
        
        alphabet_id = seed_alphabet_topic()
        time.sleep(0.5)
        
        greetings_id = seed_greetings_topic()
        time.sleep(0.5)
        
        numbers_id = seed_numbers_topic()
        
        # Summary
        print("\n" + "="*60)
        print("✅ DATABASE SEEDING COMPLETED!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Admin user created/logged in")
        print(f"  • 3 Topics created (Alphabet, Greetings, Numbers)")
        print(f"  • Multiple Levels per topic")
        print(f"  • Multiple Exercises per level")
        print(f"  • All content in pt_BR and en_US")
        print(f"\n🔗 Access the API at: http://localhost:8000/docs")
        print(f"📧 Admin credentials:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
