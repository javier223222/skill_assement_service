"""
Script para limpiar la base de datos y regenerar preguntas correctamente
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def clean_and_reset_db():
    """
    Limpia completamente la colección de preguntas para empezar desde cero
    """
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://admin:password123@54.205.187.151:27017/skill_assement?authSource=admin')
    client = AsyncIOMotorClient(mongodb_url)
    db = client['skill_assement']
    
    try:
        print("🧹 Limpiando base de datos...")
        
        # Eliminar todas las preguntas
        result = await db.questions.delete_many({})
        print(f"✅ Eliminadas {result.deleted_count} preguntas")
        
        # Eliminar todas las sesiones de usuario
        result = await db.user_sessions.delete_many({})
        print(f"✅ Eliminadas {result.deleted_count} sesiones de usuario")
        
        # Eliminar todos los feedbacks
        result = await db.assement_feedbacks.delete_many({})
        print(f"✅ Eliminados {result.deleted_count} feedbacks")
        
        print("\n🔄 Base de datos limpiada correctamente")
        print("📋 Ahora puedes crear nuevas evaluaciones sin conflictos")
        
        # Verificar que está limpia
        questions_count = await db.questions.count_documents({})
        sessions_count = await db.user_sessions.count_documents({})
        feedbacks_count = await db.assement_feedbacks.count_documents({})
        
        print(f"\n📊 Estado actual:")
        print(f"Preguntas: {questions_count}")
        print(f"Sesiones: {sessions_count}")
        print(f"Feedbacks: {feedbacks_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("⚠️  ATENCIÓN: Este script eliminará TODOS los datos de evaluaciones")
    print("🔄 Esto incluye preguntas, sesiones y feedbacks")
    
    confirm = input("\n¿Confirmas que quieres proceder? (LIMPIAR/no): ")
    if confirm.upper() == 'LIMPIAR':
        asyncio.run(clean_and_reset_db())
        print("\n✅ Operación completada. La base de datos está limpia.")
    else:
        print("❌ Operación cancelada.")
