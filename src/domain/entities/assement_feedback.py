from beanie import Document
from pydantic import BaseModel,Field
from typing import List
from datetime import datetime,timezone


class UserAnswer(BaseModel):
    answer: str
    is_correct: bool
class QuestionAnalysis(BaseModel):
    question_number: int  # Cambiar de question_id a question_number
    question: str
    subcategory: str
    correct_answer: str
    user_answers: List[UserAnswer] 


class AssementResult(BaseModel):
    subcategory: str = Field( description="The subcategory of the skill")
    percentage: float = Field( description="The score achieved in the subcategory")
class RelevantSkillToFocusOn(BaseModel):
    skill: str = Field( description="The name of the skill")
    score: float = Field( description="The score achieved in the skill")

class RecommendeToolsAndFrameWorks(BaseModel):
    name: str = Field( description="The name of the tool or framework")


class  AssementFeedback(Document):
    user_id: str = Field( index=True, description="The ID of the user associated with the feedback")
    session_id: str = Field( index=True, description="The ID of the session associated with the feedback")
    assement_result: float = Field( description="The overall score of the assessment")
    industry_avarage: float = Field( description="The average score of the industry")
    points_earned: float = Field( description="The points earned in the assessment")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    results: List[AssementResult] = Field( description="The results of the assessment")
    relevant_skills: List[RelevantSkillToFocusOn] = Field( description="Skills to focus on for improvement")
    recommended_tools: List[RecommendeToolsAndFrameWorks] = Field(  description="Tools and frameworks to assist learning")
    questions_analysis: List[QuestionAnalysis] = Field(  description="Analysis of questions with user answers")
    good_answers:float = Field( default=0, description="Number of good answers")
    bad_answers:float = Field( default=0, description="Number of bad answers")
    
    class Settings:
        name = "assement_feedback"
      
        
