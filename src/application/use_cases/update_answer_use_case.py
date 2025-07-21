

from application.dto.answer_question_dto import AnswerQuestionDTO
from application.use_cases.base_assement_use_case import BaseAssessmentUseCase

class UpdateAnswerUseCase(BaseAssessmentUseCase):

    async def execute(self, question: AnswerQuestionDTO) -> dict:
        try:
            session = await self.user_session_repository.get_user_session_by_id(question.id_session)
            find_question = await self.question_repository.get_question_by_id(question.id_question)

            if session.is_finished:
                raise Exception("Session is already finished")
            if session.user_id != question.id_user:
                raise Exception("User ID does not match the session user ID")
            if question.id_question < 0 or question.id_question > session.total_questions:
                raise Exception("Invalid question ID")
            if not session:
                raise Exception("Session not found")
            if question.id_question >= session.actual_number_of_questions:
                raise Exception("Question not answered yet")
            if not find_question:
                raise Exception("Question not found")

            for i in session.answers:
                if i.id_question == question.id_question:
                    session.answers[session.answers.index(i)] = {
                        "id_question": question.id_question,
                        "answer": question.answer
                
                    }
                    break
            

                
            session = await self.user_session_repository.update_user_session(session)


            return {
                "message": "Answer recorded successfully",
                "session_id": session,
                "current_question_number": session.actual_number_of_questions
            }

        except Exception as e:
            raise Exception(f"Error processing answer: {str(e)}")
