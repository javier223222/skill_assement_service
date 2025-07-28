"""
Script de prueba para verificar el flujo de respuestas
"""

import json

def test_answer_flow():
    """
    Simula el flujo completo de responder preguntas
    """
    
    print("🧪 Simulación del flujo de respuestas corregido:")
    print()
    
    # Simular creación de sesión
    print("1. Crear sesión:")
    session = {
        "id": "session_123",
        "user_id": "user_456", 
        "skill_id": "skill_789",
        "total_questions": 10,
        "actual_number_of_questions": 0,  # Ahora inicia en 0
        "answers": [],
        "is_finished": False
    }
    print(f"   Sesión creada: {json.dumps(session, indent=4)}")
    print()
    
    # Simular respuestas
    print("2. Responder preguntas:")
    
    questions_and_answers = [
        (1, "const"),
        (2, "arrow function"),
        (3, "let tiene scope de bloque"),
    ]
    
    for question_num, answer in questions_and_answers:
        print(f"   Pregunta {question_num}: {answer}")
        
        # Simular el proceso de AnswerQuestionUseCase
        session["actual_number_of_questions"] += 1
        session["answers"].append({
            "id_question": question_num,
            "answer": answer
        })
        
        response = {
            "message": "Answer recorded successfully",
            "session_id": session["id"],
            "question_answered": question_num,
            "total_questions": session["total_questions"],
            "questions_answered": session["actual_number_of_questions"],
            "is_completed": session["actual_number_of_questions"] >= session["total_questions"],
            "next_question": session["actual_number_of_questions"] + 1 if session["actual_number_of_questions"] < session["total_questions"] else None
        }
        
        print(f"   Respuesta: {json.dumps(response, indent=6)}")
        print()
    
    print("3. Estado final de la sesión:")
    print(f"   {json.dumps(session, indent=4)}")
    print()
    
    print("✅ Flujo simulado completamente!")
    print()
    print("📋 Cambios implementados:")
    print("   - AnswerSessionModel ahora se accede como objeto (.id_question)")
    print("   - Sesión inicia con actual_number_of_questions = 0")
    print("   - Se incrementa después de cada respuesta")
    print("   - Validaciones actualizadas para usar números 1-10")
    print("   - Respuestas más informativas")

if __name__ == "__main__":
    test_answer_flow()
