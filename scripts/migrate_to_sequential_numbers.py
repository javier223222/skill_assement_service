"""
Script para migrar preguntas existentes al nuevo formato con question_number secuencial
SEGURO PARA PRODUCCIÓN
"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

async def migrate_question_numbers():
    """
    Migra las preguntas existentes para usar question_number secuencial (1, 2, 3, etc.)
    """
    # Conectar a MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@54.205.187.151:27017/skill_assement?authSource=admin")
    db_name = os.getenv("MONGODB_DB_NAME", "skill_assement")
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]
    questions_collection = db["questions"]
    
    try:
        # Obtener todas las skills únicas
        skills = await questions_collection.distinct("skillid")
        print(f"Encontradas {len(skills)} skills con preguntas para migrar")
        
        total_migrated = 0
        
        for skill_id in skills:
            print(f"\nMigrando preguntas para skill: {skill_id}")
            
            # Obtener todas las preguntas de esta skill, ordenadas por fecha de creación
            questions = await questions_collection.find(
                {"skillid": skill_id}
            ).sort("created_at", 1).to_list(length=None)
            
            print(f"  Encontradas {len(questions)} preguntas")
            
            # Asignar números secuenciales
            for index, question in enumerate(questions, 1):
                # Actualizar cada pregunta con su nuevo question_number
                await questions_collection.update_one(
                    {"_id": question["_id"]},
                    {
                        "$set": {"question_number": index},
                        "$unset": {"id": ""}  # Eliminar el campo id antiguo si existe
                    }
                )
                print(f"    Pregunta {question['_id']} -> question_number: {index}")
                total_migrated += 1
        
        print(f"\n✅ Migración completada. Total de preguntas migradas: {total_migrated}")
        
        # Verificar la migración
        sample_questions = await questions_collection.find({}).limit(5).to_list(length=5)
        print("\n📋 Muestra de preguntas migradas:")
        for q in sample_questions:
            print(f"  Skill: {q.get('skillid', 'N/A')}, Question Number: {q.get('question_number', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error en migración: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🔄 Migrando preguntas al formato con question_number secuencial")
    print("📋 Esta operación es segura y preserva los datos")
    print("🔢 Las preguntas se numerarán 1, 2, 3, etc. por skill")
    
    confirm = input("\n¿Confirmas que quieres proceder? (si/no): ")
    if confirm.lower() in ['si', 'sí', 'yes', 'y']:
        asyncio.run(migrate_question_numbers())
        print("\n✅ Migración completada. Reinicia el servicio para aplicar los cambios.")
    else:
        print("❌ Operación cancelada.")
