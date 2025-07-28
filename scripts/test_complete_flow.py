"""
Script para probar el flujo completo de evaluación después del fix
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_complete_assessment_flow():
    """
    Prueba el flujo completo: crear evaluación, responder preguntas, generar feedback
    """
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Iniciando prueba del flujo completo de evaluación")
        print("=" * 60)
        
        # 1. Obtener skills disponibles
        print("\n1️⃣ Obteniendo skills disponibles...")
        async with session.get(f"{BASE_URL}/skills") as response:
            if response.status == 200:
                skills = await response.json()
                if skills:
                    skill_id = skills[0]["id"]
                    skill_name = skills[0]["name"]
                    print(f"✅ Skill encontrado: {skill_name} (ID: {skill_id})")
                else:
                    print("❌ No hay skills disponibles")
                    return
            else:
                print(f"❌ Error obteniendo skills: {response.status}")
                return
        
        # 2. Crear evaluación
        print("\n2️⃣ Creando nueva evaluación...")
        assessment_data = {
            "skill_id": skill_id,
            "user_id": "test_user_123"
        }
        
        async with session.post(f"{BASE_URL}/assessments/create", 
                              json=assessment_data) as response:
            if response.status == 200:
                assessment_result = await response.json()
                session_id = assessment_result["session"]["id"]
                print(f"✅ Evaluación creada exitosamente")
                print(f"   Session ID: {session_id}")
                print(f"   Total preguntas: {assessment_result['session']['total_questions']}")
            else:
                error_text = await response.text()
                print(f"❌ Error creando evaluación: {response.status}")
                print(f"   Detalle: {error_text}")
                return
        
        # 3. Obtener primera pregunta
        print("\n3️⃣ Obteniendo primera pregunta...")
        async with session.get(f"{BASE_URL}/assessments/{session_id}/question/1") as response:
            if response.status == 200:
                question_data = await response.json()
                print(f"✅ Pregunta obtenida:")
                print(f"   Número: {question_data['question_number']}")
                print(f"   Pregunta: {question_data['question'][:80]}...")
                print(f"   Opciones: {len(question_data['options'])}")
                
                # Usar la primera opción como respuesta de prueba
                test_answer = question_data['options'][0]
            else:
                error_text = await response.text()
                print(f"❌ Error obteniendo pregunta: {response.status}")
                print(f"   Detalle: {error_text}")
                return
        
        # 4. Responder preguntas (responder todas con la primera opción)
        print("\n4️⃣ Respondiendo todas las preguntas...")
        total_questions = assessment_result['session']['total_questions']
        
        for question_num in range(1, total_questions + 1):
            # Obtener pregunta
            async with session.get(f"{BASE_URL}/assessments/{session_id}/question/{question_num}") as response:
                if response.status == 200:
                    question_data = await response.json()
                    test_answer = question_data['options'][0]  # Primera opción
                    
                    # Responder pregunta
                    answer_data = {
                        "session_id": session_id,
                        "question_number": question_num,
                        "answer": test_answer
                    }
                    
                    async with session.put(f"{BASE_URL}/assessments/answer", 
                                         json=answer_data) as answer_response:
                        if answer_response.status == 200:
                            print(f"   ✅ Pregunta {question_num} respondida")
                        else:
                            error_text = await answer_response.text()
                            print(f"   ❌ Error respondiendo pregunta {question_num}: {answer_response.status}")
                            print(f"      Detalle: {error_text}")
                            return
                else:
                    print(f"   ❌ Error obteniendo pregunta {question_num}: {response.status}")
                    return
        
        # 5. Generar feedback
        print("\n5️⃣ Generando feedback...")
        feedback_data = {"session_id": session_id}
        
        async with session.post(f"{BASE_URL}/assessments/evaluate", 
                              json=feedback_data) as response:
            if response.status == 200:
                feedback_result = await response.json()
                print(f"✅ Feedback generado exitosamente")
                print(f"   Score general: {feedback_result.get('overall_score', 'N/A')}")
                print(f"   Puntos: {feedback_result.get('points_earned', 'N/A')}")
                print(f"   Promedio industria: {feedback_result.get('industry_average', 'N/A')}")
            else:
                error_text = await response.text()
                print(f"❌ Error generando feedback: {response.status}")
                print(f"   Detalle: {error_text}")
                return
        
        print("\n🎉 ¡Flujo completo ejecutado exitosamente!")
        print("=" * 60)
        print("✅ Todos los errores de validación Pydantic han sido resueltos")

if __name__ == "__main__":
    print(f"🕐 Iniciando prueba: {datetime.now()}")
    asyncio.run(test_complete_assessment_flow())
