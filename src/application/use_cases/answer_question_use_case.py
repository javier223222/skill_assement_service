
from application.dto.answer_question_dto import AnswerQuestionDTO
from datetime import datetime, timezone 

from application.use_cases.base_assement_use_case import BaseAssessmentUseCase
class AnswerQuestionUseCase(BaseAssessmentUseCase):
    async def execute(self, question: AnswerQuestionDTO) -> dict:
        try:

            session=await self.user_session_repository.get_user_session_by_id(question.id_session)
            find_question=await self.question_repository.get_question_by_id(question.id_question)
        
            if(session.is_finished):
                raise Exception("Session is already finished")
            if (session.user_id != question.id_user):
                raise Exception("User ID does not match the session user ID")
          
            for existing_answer in session.answers:
                if existing_answer["id_question"] == question.id_question:
                    raise Exception("Question already answered")
            
            if(question.id_question < 1 or question.id_question > session.total_questions):
                raise Exception("Invalid question ID")
            if not session:
                raise Exception("Session not found")
            if question.id_question < session.actual_number_of_questions:
                raise Exception("Question already answered")
            if not find_question:
                raise Exception("Question not found")
            
            
            if session.actual_number_of_questions == session.total_questions:
                session.is_finished = True
                session.finished_at = datetime.now(timezone.utc)
                session.status = "completed"
            else:
                session.actual_number_of_questions += 1
                session.updated_at = datetime.now(timezone.utc)
            
            

            



            
            

            session.answers.append({
                "id_question": question.id_question,
                
                "answer": question.answer
            })
            session=await self.user_session_repository.update_user_session(session)
            return {
                "message": "Answer recorded successfully",
                "session_id": str(session.id),
                "next_question": session.actual_number_of_questions
            }



            
                
                
            

        
            
            
        except Exception as e:
            raise Exception(f"Error processing answer: {str(e)}")

