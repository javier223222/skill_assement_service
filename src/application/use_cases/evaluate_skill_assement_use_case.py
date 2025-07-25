from domain.repositories.question_repository import QuestionRepository
from domain.repositories.user_session_repository import UserSessionRepository
from domain.repositories.assement_feedback_repository import AssementFeedBackRepository
from domain.entities.assement_feedback import AssementFeedback,AssementResult,RelevantSkillToFocusOn,RecommendeToolsAndFrameWorks,QuestionAnalysis
from infrastructure.messaging.rabbitmq_producer import RabbitMQProducer
from datetime import datetime
from typing import List
from typing import Dict, Any

class EvaluateSkillAssessment:
    def __init__(self, user_session_repository: UserSessionRepository, question_repository: QuestionRepository, feedback_repository: AssementFeedBackRepository, rabbitmq_producer: RabbitMQProducer):
        self.user_session_repository = user_session_repository
        self.question_repository = question_repository
        self.feedback_repository = feedback_repository
        self.rabbitmq_producer = rabbitmq_producer

    async def execute(self, session_id: str) -> Dict[str, Any]:
     try:
        session = await self.user_session_repository.get_user_session_by_id(session_id)
        feedBackbySessionId= await self.feedback_repository.get_feedback_by_session_id(session_id)
        questions = await self.question_repository.find_questions_by_skillid(session.skill_id)
        
        if feedBackbySessionId:
            

            return {
                "message": "Ya se ha evaluado esta sesión",
                "session_id": session_id,
                "feedback": feedBackbySessionId
            }
        
        
        if not session:
            raise Exception("Session not found")
        if not session.is_finished:
            raise Exception("Session is not finished")
        
      
        if not questions:
            raise Exception("No questions found for the skill")

        
        
        
        category_scores = self.calculate_percentage_by_category(questions, session.answers)
        overall_score = self.calculate_overall_score(category_scores)
        recommend_tools:List[RecommendeToolsAndFrameWorks] = []
        question_analysis, good_answers, bad_answers = self.calculate_question_with_good_or_bad_answers(questions, session.answers)
        industry_average = self.calculate_industry_average(category_scores)
        points = self.calculte_points(category_scores)
        relevant_skills: List[RelevantSkillToFocusOn] = self.get_relevant_skills_focus_on(category_scores)

        if questions[0].recommended_tools:
            for tool in questions[0].recommended_tools:
                recommend_tools.append(
                    RecommendeToolsAndFrameWorks(name=tool)
                )
        
        assement_feedback = AssementFeedback(
            user_id=session.user_id,
            session_id=str(session.id),
            assement_result=overall_score,
            industry_avarage=industry_average,
            points_earned=points,
            results=category_scores,
            relevant_skills=relevant_skills,
            recommended_tools=recommend_tools,
            questions_analysis=question_analysis,
            bad_answers=bad_answers,
            good_answers=good_answers

        )
        await self.rabbitmq_producer.publish_message(
            message={
            "event": "Skill Assement Finished",
            "type": "Skill Assement",
            "created_at": str(datetime.utcnow()),
            "points_earned": points,
            "user_id": session.user_id,
            },
            queue_name="any",
            priority=5

        )
        feedback = await self.feedback_repository.create_feedback(assement_feedback)


        return {
            "session_id": str(session.id),
            "user_id": session.user_id,
            "skill_id": session.skill_id,
            "assement_result": feedback.assement_result,
            "result": category_scores,
            "industry_average": feedback.industry_avarage,
            "points": feedback.points_earned,
        

            "relevant_skills": feedback.relevant_skills,
            "recommended_tools": feedback.recommended_tools,
            "questions_analysis": feedback.questions_analysis,
            "good_answers": feedback.good_answers,
            "bad_answers": feedback.bad_answers,

            "total_questions": len(questions),
            "total_answered": len(session.answers)
        }
     except Exception as e:
        print(f"Error evaluating skill assessment: {str(e)}")
        raise Exception(f"Error evaluating skill assessment: {str(e)}")

    def calculate_percentage_by_category(self, questions: list, answers: list) -> List[AssementResult]:
        """Calcular porcentaje de aciertos por categoría"""
        category_scores = []
        
       
    
        category_data = {}
       
        for question in questions:
            category = question.subcategory
            if category not in category_data:
                category_data[category] = {"correct": 0, "total": 0}
        
    
        for question in questions:
            category = question.subcategory
            category_data[category]["total"] += 1
            
            for answer in answers:
             if answer.id_question == question.id:
                if answer.answer == question.correct_answer:
                    category_data[category]["correct"] += 1
                break
        
       
        category_scores = []
        for category, data in category_data.items():
            percentage = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0
            category_scores.append(
            AssementResult(
                subcategory=category,
                percentage=percentage
                
            )
            )
        
        return category_scores
    
    def calculate_overall_score(self, category_scores: List[AssementResult]) -> float:
        """Calcular puntaje general promediando las categorías"""
        if not category_scores:
            return 0.0
        
        total_score = sum(score.percentage for score in category_scores)
        return total_score / len(category_scores)
    def calculate_question_with_good_or_bad_answers(self, questions: list, answers: list) -> tuple[List[QuestionAnalysis], int, int]:
        """Calcular preguntas con respuestas buenas o malas"""
        question_analysis: List[QuestionAnalysis] = []
        good_answers = 0
        bad_answers = 0

        for question in questions:
            analysis_item = QuestionAnalysis(
                question_id=question.id,
                question=question.question,
                subcategory=question.subcategory,
                correct_answer=question.correct_answer,
                user_answers=[]
            )
            question_analysis.append(analysis_item)

        questions_map = {question.id: question for question in questions}
        
       
        for question in questions:
            
            question_analysis.append(analysis_item)
        
       
        for answer in answers:
            if answer.id_question in questions_map:
                
                for item in question_analysis:
                    if item.question_id == answer.id_question:
                        is_correct = answer.answer == item.correct_answer
                        item.user_answers.append({
                            "answer": answer.answer,
                            "is_correct": is_correct
                        })
                        if is_correct:
                            good_answers += 1
                        else:
                            bad_answers += 1
                        break
        
        return question_analysis, good_answers, bad_answers
    def calculate_industry_average(self, category_scores: List[AssementResult]) -> float:
        """Calcular promedio de la industria"""
        if not category_scores:
            return 0.0

        total_score = sum(score.percentage for score in category_scores)
        return total_score / len(category_scores)
    def get_relevant_skills_focus_on(self, category_scores: List[AssementResult]) -> List[RelevantSkillToFocusOn]:
        """Obtener habilidades relevantes para enfocarse"""
        relevant_skills = []
        for score in category_scores:
            if score.percentage < 50:
                relevant_skills.append({
                    "skill": score.subcategory,
                    "score": score.percentage
                })
        return relevant_skills
    def calculte_points(self, category_scores: List[AssementResult]) -> int:
        """Calcular puntos basados en los puntajes de las categorías"""
        points = 0
        for item in category_scores:
            score = item.percentage
            if score >= 90:
                points += 10
            elif score >= 75:
                points += 5
            elif score >= 50:
                points += 2
            else:
                points += 1
        return points
  