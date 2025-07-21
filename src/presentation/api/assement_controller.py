from fastapi import APIRouter, HTTPException,status


from domain.repositories.question_repository import QuestionRepository
from domain.repositories.user_session_repository import UserSessionRepository
from domain.repositories.assement_feedback_repository import AssementFeedBackRepository
from domain.repositories.skill_repository import SkillRepository
from infrastructure.external_services.gemini_service import GeminiService
from application.use_cases.create_assement_use_case import CreateAssessmentUseCase
from application.use_cases.answer_question_use_case import AnswerQuestionUseCase
from application.dto.answer_question_dto import AnswerQuestionDTO,AnswerQuestionBaseDto
from domain.repositories.skill_repository import SkillRepository
from ..schemas.start_assement_model import StartAssessmentModel
from infrastructure.messaging.rabbitmq_producer import rabbitmq_producer

from ..schemas.answer_question_model import AnswerQuestionModel



from application.use_cases.update_answer_use_case import UpdateAnswerUseCase
from application.use_cases.get_question_use_case import GetQuestionUseCase
from application.use_cases.evaluate_skill_assement_use_case import EvaluateSkillAssessment
from application.use_cases.get_feedbacks_by_user import GetFeedbacksByUser
from application.use_cases.get_feedback_by_id_use_case import GetFeedBackByIdUseCase
assement_router = APIRouter(prefix="/assement",tags=["questions"])
@assement_router.post("/{skill_id}", status_code=status.HTTP_201_CREATED)
async def create_question(skill_id: str,request: StartAssessmentModel):
    try:
        question_repository = QuestionRepository()
        skill_repository = SkillRepository()
        gemini_service = GeminiService()
        user_session_repository = UserSessionRepository()
        create_assessment_use_case = CreateAssessmentUseCase(question_repository, gemini_service,skill_repository,user_session_repository)

        generated_assement = await create_assessment_use_case.execute(skill_id,request.id_user)

        return {
            "message": "Assessment generated successfully",
            "Assessment": generated_assement,
            "next_step":1
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@assement_router.get("/session/{session_id}")
async def get_session(session_id: str):
    try:
        user_session_repository = UserSessionRepository()
        session = await user_session_repository.get_user_session_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@assement_router.get("/questions/{id}")
async def get_questions_by_id(id:int,id_user: str,id_session: str):
    try:
        
       get_all_skills_use_case = GetQuestionUseCase(QuestionRepository(), UserSessionRepository())


       questions = await get_all_skills_use_case.execute(AnswerQuestionBaseDto(
            id_session=id_session,
            id_user=id_user,
            id_question=id
        ))
       
       if not questions:
            raise HTTPException(status_code=404, detail="No questions found for this skill")
        
       return questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@assement_router.post("/questions/{id_question}", status_code=status.HTTP_201_CREATED)
async def answer_question(id_question: int, request: AnswerQuestionModel):
    try:
        answer_question_use_case = AnswerQuestionUseCase(QuestionRepository(), UserSessionRepository())
        result = await answer_question_use_case.execute(AnswerQuestionDTO(
            id_question=id_question,
            id_session=request.id_session,
            id_user=request.id_user,
            answer=request.answer
        ))

        return result


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@assement_router.put("/questions/{id_question}", status_code=status.HTTP_200_OK)
async def update_answer(id_question: int, request: AnswerQuestionModel):
    try:
        answer_question_use_case = UpdateAnswerUseCase(QuestionRepository(), UserSessionRepository())
        result = await answer_question_use_case.execute(AnswerQuestionDTO(
            id_question=id_question,
            id_session=request.id_session,
            id_user=request.id_user,
            answer=request.answer
        ))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@assement_router.get("/feedback/{session_id}")
async def get_feedback(session_id: str):
    try:
        generate_feedback_use_case = EvaluateSkillAssessment(
            user_session_repository=UserSessionRepository(),
            question_repository=QuestionRepository(),
            feedback_repository=AssementFeedBackRepository(),
            rabbitmq_producer=rabbitmq_producer
        )
        
        session = await generate_feedback_use_case.execute(session_id)


        
    
        return session

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@assement_router.get("/feedbacks/{user_id}")
async def get_feedbacks_by_user(user_id: str, skip: int = 0, limit: int = 10):
    try:
        get_feedbacks_use_case = GetFeedbacksByUser(
            user_session_repository=UserSessionRepository(),
            feedback_repository=AssementFeedBackRepository(),
            skill_repository=SkillRepository()
        )
        feedbacks = await get_feedbacks_use_case.execute(user_id, skip, limit)

        return feedbacks

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
                          
@assement_router.get("/feedback/assement/{feedback_id}")
async def get_feedback_by_id(feedback_id: str):
    try:
        feedback_repository = AssementFeedBackRepository()
        skill_repository = SkillRepository()
        user_session_repository = UserSessionRepository()
        get_feedback_by_id_use_case = GetFeedBackByIdUseCase(feedback_repository, skill_repository, user_session_repository)

        feedback = await get_feedback_by_id_use_case.execute(feedback_id)
        
        
        
        return feedback

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))