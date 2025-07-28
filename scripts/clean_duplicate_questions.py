"""
Script para limpiar preguntas duplicadas en desarrollo
USAR SOLO EN AMBIENTE DE DESARROLLO
"""

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

async def clean_duplicate_questions():
    """
    Limpia las preguntas duplicadas de la base de datos
    """
    # Conectar a MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "skill_assement")
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[db_name]
    questions_collection = db["questions"]
    
    try:
        # Eliminar todas las preguntas para empezar limpio
        result = await questions_collection.delete_many({})
        print(f"Eliminadas {result.deleted_count} preguntas duplicadas")
        
        # Verificar que no hay documentos
        count = await questions_collection.count_documents({})
        print(f"Preguntas restantes en la colección: {count}")
        
    except Exception as e:
        print(f"Error limpiando preguntas: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("⚠️  ADVERTENCIA: Este script eliminará TODAS las preguntas")
    print("🔄 Úsalo solo en ambiente de desarrollo")
    
    confirm = input("¿Confirmas que quieres proceder? (si/no): ")
    if confirm.lower() in ['si', 'sí', 'yes', 'y']:
        asyncio.run(clean_duplicate_questions())
        print("✅ Limpieza completada. Ahora puedes generar nuevas evaluaciones.")
    else:
        print("❌ Operación cancelada.")
