

from application.dto.answer_question_dto import AnswerQuestionBaseDto
from application.use_cases.base_assement_use_case import BaseAssessmentUseCase

class GetQuestionUseCase(BaseAssessmentUseCase):
    async def execute(self, question: AnswerQuestionBaseDto) -> dict:
      try:
         
      
          session=await self.user_session_repository.get_user_session_by_id(question.id_session)
          find_question=await self.question_repository.get_question_by_id(question.id_question)
         
          if(session.is_finished):
                raise Exception("Session is already finished")
          if (session.user_id != question.id_user):
                raise Exception("User ID does not match the session user ID")
            
            
          if(question.id_question < 1 or question.id_question > session.total_questions):
                raise Exception("Invalid question ID")
          if not session:
                raise Exception("Session not found")
         
          if not find_question:
                raise Exception("Question not found")
          if not question:
            raise Exception("Question not found")
          return {
            "id": find_question.question_number,
            "text": find_question.question,
            "options": find_question.options,
            "subcategory": find_question.subcategory,
            "type": find_question.type,
            "recommended_tools": find_question.recommended_tools,
            "has_next": question.id_question < session.total_questions,
            "has_previous": question.id_question > 1,
            "next_question_id": question.id_question + 1 if question.id_question < session.total_questions else None,
          }
      except Exception as e:
            
            raise Exception(f"Error retrieving question: {str(e)}")