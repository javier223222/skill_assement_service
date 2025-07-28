

from application.dto.answer_question_dto import AnswerQuestionDTO
from application.use_cases.base_assement_use_case import BaseAssessmentUseCase
from domain.entities.user_session import AnswerSessionModel

class UpdateAnswerUseCase(BaseAssessmentUseCase):

    async def execute(self, question: AnswerQuestionDTO) -> dict:
        try:
            session = await self.user_session_repository.get_user_session_by_id(question.id_session)
            find_question = await self.question_repository.get_question_by_id(question.id_question)

            if session.is_finished:
                raise Exception("Session is already finished")
            if session.user_id != question.id_user:
                raise Exception("User ID does not match the session user ID")
            if question.id_question < 1 or question.id_question > session.total_questions:
                raise Exception("Invalid question ID")
            if not session:
                raise Exception("Session not found")
            if question.id_question > session.actual_number_of_questions:
                raise Exception("Question not answered yet")
            if not find_question:
                raise Exception("Question not found")

            # Buscar y actualizar la respuesta existente
            for i, answer in enumerate(session.answers):
                if answer.id_question == question.id_question:
                    # Crear nuevo objeto AnswerSessionModel con la respuesta actualizada
                    updated_answer = AnswerSessionModel(
                        id_question=question.id_question,
                        answer=question.answer
                    )
                    session.answers[i] = updated_answer
                    break
            else:
                # Si no se encontró la respuesta, significa que no ha sido respondida aún
                raise Exception("Question not answered yet")
            

                
            session = await self.user_session_repository.update_user_session(session)


            return {
                "message": "Answer updated successfully",
                "session_id": str(session.id),
                "current_question_number": session.actual_number_of_questions
            }

        except Exception as e:
            raise Exception(f"Error processing answer: {str(e)}")
