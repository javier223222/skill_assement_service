"""
Script de prueba simple para verificar el flujo de evaluación paso a paso
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_step_by_step():
    """
    Prueba cada paso del flujo individualmente para identificar dónde falla
    """
    print("🧪 Prueba paso a paso del flujo de evaluación")
    print("=" * 50)
    
    try:
        # 1. Obtener skills
        print("\n1️⃣ Obteniendo skills...")
        response = requests.get(f"{BASE_URL}/skills")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            skills = response.json()
            if skills:
                skill_id = skills[0]["id"]
                skill_name = skills[0]["name"]
                print(f"✅ Skill: {skill_name} (ID: {skill_id})")
            else:
                print("❌ No hay skills disponibles")
                return
        else:
            print(f"❌ Error: {response.text}")
            return
            
        # 2. Crear evaluación
        print("\n2️⃣ Creando evaluación...")
        assessment_data = {
            "skill_id": skill_id,
            "user_id": "test_user_debug"
        }
        
        response = requests.post(f"{BASE_URL}/assessments/create", json=assessment_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session"]["id"]
            total_questions = result["session"]["total_questions"]
            print(f"✅ Evaluación creada")
            print(f"   Session ID: {session_id}")
            print(f"   Total preguntas: {total_questions}")
        else:
            print(f"❌ Error creando evaluación:")
            print(response.text)
            return
            
        # 3. Verificar sesión directamente
        print("\n3️⃣ Verificando sesión creada...")
        print(f"Session ID para verificar: {session_id}")
        
        # 4. Obtener primera pregunta
        print("\n4️⃣ Obteniendo primera pregunta...")
        response = requests.get(f"{BASE_URL}/assessments/{session_id}/question/1")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            question = response.json()
            print(f"✅ Pregunta obtenida:")
            print(f"   Número: {question['question_number']}")
            print(f"   Texto: {question['question'][:80]}...")
            
            # Usar primera opción como respuesta
            answer = question['options'][0]
            print(f"   Respuesta de prueba: {answer}")
        else:
            print(f"❌ Error obteniendo pregunta:")
            print(response.text)
            return
            
        # 5. Responder pregunta
        print("\n5️⃣ Respondiendo pregunta...")
        answer_data = {
            "session_id": session_id,
            "question_number": 1,
            "answer": answer
        }
        
        response = requests.put(f"{BASE_URL}/assessments/answer", json=answer_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Pregunta respondida")
        else:
            print(f"❌ Error respondiendo:")
            print(response.text)
            return
            
        # 6. Responder todas las demás preguntas rápidamente
        print(f"\n6️⃣ Respondiendo las {total_questions-1} preguntas restantes...")
        for q_num in range(2, total_questions + 1):
            # Obtener pregunta
            response = requests.get(f"{BASE_URL}/assessments/{session_id}/question/{q_num}")
            if response.status_code == 200:
                question = response.json()
                answer = question['options'][0]
                
                # Responder
                answer_data = {
                    "session_id": session_id,
                    "question_number": q_num,
                    "answer": answer
                }
                
                response = requests.put(f"{BASE_URL}/assessments/answer", json=answer_data)
                if response.status_code == 200:
                    print(f"   ✅ Pregunta {q_num} respondida")
                else:
                    print(f"   ❌ Error en pregunta {q_num}: {response.text}")
                    return
            else:
                print(f"   ❌ Error obteniendo pregunta {q_num}: {response.text}")
                return
                
        # 7. PUNTO CRÍTICO: Intentar generar feedback
        print("\n7️⃣ GENERANDO FEEDBACK (punto crítico)...")
        print(f"Session ID a evaluar: {session_id}")
        
        feedback_data = {"session_id": session_id}
        response = requests.post(f"{BASE_URL}/assessments/evaluate", json=feedback_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            feedback = response.json()
            print("✅ ¡FEEDBACK GENERADO EXITOSAMENTE!")
            print(f"   Score: {feedback.get('overall_score', 'N/A')}")
        else:
            print("❌ ERROR AL GENERAR FEEDBACK:")
            print(response.text)
            
            # Información adicional para debug
            print(f"\n🔍 Debug info:")
            print(f"   Session ID usado: {session_id}")
            print(f"   Endpoint llamado: {BASE_URL}/assessments/evaluate")
            print(f"   Payload enviado: {feedback_data}")
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_step_by_step()
