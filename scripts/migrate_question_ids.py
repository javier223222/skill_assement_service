"""
Script para migrar preguntas existentes sin perder datos
SEGURO PARA PRODUCCIÓN
"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
import time
import random

async def migrate_question_ids():
    """
    Migra las preguntas existentes asignando nuevos IDs únicos
    """
    # Conectar a MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "skill_assement")
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]
    questions_collection = db["questions"]
    
    try:
        # Obtener todas las preguntas
        questions = await questions_collection.find({}).to_list(length=None)
        print(f"Encontradas {len(questions)} preguntas para migrar")
        
        # Crear un mapeo de IDs antiguos a nuevos
        id_mapping = {}
        migrated_questions = []
        
        for question in questions:
            # Generar nuevo ID único
            new_id = int(time.time() * 1000000) + random.randint(1000, 9999)
            
            # Asegurar unicidad
            while new_id in [q['id'] for q in migrated_questions]:
                new_id = int(time.time() * 1000000) + random.randint(1000, 9999)
            
            # Mapear ID antiguo a nuevo
            old_id = question.get('id', question['_id'])
            id_mapping[old_id] = new_id
            
            # Crear nueva pregunta con ID único
            new_question = question.copy()
            new_question['id'] = new_id
            migrated_questions.append(new_question)
        
        # Eliminar preguntas existentes
        await questions_collection.delete_many({})
        print("Preguntas existentes eliminadas")
        
        # Insertar preguntas migradas
        if migrated_questions:
            await questions_collection.insert_many(migrated_questions)
            print(f"Insertadas {len(migrated_questions)} preguntas con nuevos IDs")
        
        # Mostrar mapeo de IDs
        print("\\nMapeo de IDs:")
        for old_id, new_id in id_mapping.items():
            print(f"  {old_id} -> {new_id}")
            
    except Exception as e:
        print(f"Error en migración: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🔄 Migrando IDs de preguntas para evitar duplicados")
    print("📋 Esta operación es segura y preserva los datos")
    
    asyncio.run(migrate_question_ids())
    print("✅ Migración completada.")
