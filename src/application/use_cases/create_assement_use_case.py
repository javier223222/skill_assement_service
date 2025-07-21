from domain.entities.question import Question
from domain.repositories.question_repository import QuestionRepository
from domain.repositories.skill_repository import SkillRepository
from domain.repositories.user_session_repository import UserSessionRepository
from domain.entities.user_session import UserSession
from infrastructure.external_services.gemini_service import GeminiService

import asyncio
class CreateAssessmentUseCase:
    def __init__(self, question_repository: QuestionRepository,gemini_service:GeminiService,skill_repository:SkillRepository,
                 user_session_repository: UserSessionRepository):
        
        self.question_repository = question_repository
        self.skill_repository = skill_repository
        self.user_session_repository = user_session_repository
        self.gemini_service = gemini_service


    async def execute(self, skill_id: str,user_id: str) :
      try:
        skill = await self.skill_repository.find_skill_by_id(skill_id)
        if not skill:
            raise Exception(f"Skill with id '{skill_id}' not found.")
        
        findAquiz = await self.question_repository.find_question_by_skillid_and_number(skill_id, 1)
        
        if findAquiz is None or findAquiz == []:
            
            generated_question = await self.gemini_service.generate_quiz_with_retry(skill.name, max_retries=5)
            
            
            if not generated_question or "questions" not in generated_question:
                
                return await self.handle_quiz_generation_failure(skill_id, user_id, skill.name)
            
            
            for i, question in enumerate(generated_question["questions"]):
                question_data = {
                    "id": question.get("id"),
                    "skillid": str(skill.id),
                    "subcategory": question.get("subcategory"),
                    "type": question.get("type"),
                    "question": question.get("question"),
                    "options": question.get("options", []),
                    "correct_answer": question.get("correct_answer"),
                    "recommended_tools": question.get("recommended_tools", []) if i == 0 else None
                }
                await self.question_repository.create_question(question_data)
                await asyncio.sleep(0.1)  

        findAquiz = await self.question_repository.find_question_by_skillid_and_number(skill_id, 1)
        total_questions = await self.question_repository.count_questions_by_skillid(skill_id)
        print(findAquiz)
        session = UserSession(
            user_id=user_id,
            skill_id=skill_id,
            total_questions=total_questions,
            actual_number_of_questions=1
        )

        session = await self.user_session_repository.create_user_session(session)
        
        return {
            "session": session,
            "skill_id": skill_id,
            "status": "success"
        }
        
      except Exception as e:
        raise Exception(f"Error generating question: {str(e)}")
    
    async def handle_quiz_generation_failure(self, skill_id: str, user_id: str, skill_name: str):
        """Handle quiz generation failure by creating a session without questions."""
        
        # Opción 1: Crear sesión sin preguntas y generar después
        session = UserSession(
            user_id=user_id,
            skill_id=skill_id,
            total_questions=0,
            actual_number_of_questions=0,
            status="pending_questions"
        )
   
    
        session = await self.user_session_repository.create_user_session(session)
    
        return {
        "session": session,
        "skill_id": skill_id,
        "status": "pending",
        "message": "Quiz generation is temporarily unavailable. Please try again in a few minutes.",
        "retry_after": 300  # 5 minutos
        }