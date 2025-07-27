
from application.dto.answer_question_dto import AnswerQuestionDTO
from datetime import datetime, timezone 
from ...infrastructure.security import ContextualValidator, ValidationContext, BusinessRuleValidator
from pydantic import ValidationError

from application.use_cases.base_assement_use_case import BaseAssessmentUseCase
class AnswerQuestionUseCase(BaseAssessmentUseCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = ContextualValidator()
        self.business_validator = BusinessRuleValidator()
    
    async def execute(self, question: AnswerQuestionDTO) -> dict:
        try:
            # Validación contextual de la respuesta
            context = ValidationContext(
                operation_type="answer_question",
                entity_type="answer",
                user_id=question.id_user,
                entity_data=question.dict()
            )
            
            validation_result = await self.validator.validate(context)
            if not validation_result.is_valid:
                raise ValidationError(validation_result.errors)

            session=await self.user_session_repository.get_user_session_by_id(question.id_session)
            find_question=await self.question_repository.get_question_by_id(question.id_question)
        
            if not session:
                raise ValidationError("Session not found")
            
            # Validaciones de reglas de negocio usando el BusinessRuleValidator
            if not await self.business_validator.validate_session_ownership(session, question.id_user):
                raise ValidationError("User ID does not match the session user ID")
                
            if not await self.business_validator.validate_session_state(session):
                raise ValidationError("Session is already finished")
            
            if not await self.business_validator.validate_question_not_answered(session, question.id_question):
                raise ValidationError("Question already answered")
                
            if not await self.business_validator.validate_question_sequence(session, question.id_question):
                raise ValidationError("Invalid question ID")
          
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

