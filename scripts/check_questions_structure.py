"""
Script para verificar la estructura actual de las preguntas en MongoDB
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_questions():
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://admin:password123@54.205.187.151:27017/skill_assement?authSource=admin')
    client = AsyncIOMotorClient(mongodb_url)
    db = client['skill_assement']
    
    try:
        print("🔍 Verificando estructura de preguntas en MongoDB...")
        
        # Obtener algunas preguntas de muestra
        questions = await db.questions.find({}).limit(5).to_list(length=5)
        
        print(f"📊 Total de preguntas encontradas: {len(questions)}")
        print("\n📋 Estructura actual de preguntas:")
        
        for i, q in enumerate(questions, 1):
            print(f"\n--- Pregunta {i} ---")
            print(f"_id: {q.get('_id')} (tipo: {type(q.get('_id'))})")
            print(f"question_number: {q.get('question_number')}")
            print(f"skillid: {q.get('skillid')}")
            print(f"question: {q.get('question', 'N/A')[:50]}...")
            
        # Verificar si hay preguntas con _id numérico
        numeric_id_count = await db.questions.count_documents({"_id": {"$type": "number"}})
        object_id_count = await db.questions.count_documents({"_id": {"$type": "objectId"}})
        
        print(f"\n📈 Estadísticas de IDs:")
        print(f"Preguntas con _id numérico: {numeric_id_count}")
        print(f"Preguntas con _id ObjectId: {object_id_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_questions())
