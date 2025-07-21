from beanie import Document
from pydantic import BaseModel
from pydantic import Field
from typing import Optional,Dict,List
from datetime import datetime,timezone

class AnswerSessionModel(BaseModel):
    id_question: int
   
    answer: str

class UserSession(Document):
    user_id:str= Field(index=True, description="The ID of the user associated with the session")
    skill_id:str= Field(index=True, description="The ID of the skill being assessed in the session")
    answers:Optional[List[AnswerSessionModel]] = Field(default=[], description="List of answers provided by the user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_questions: int = Field(0, description="Total number of questions in the session")
    
    percentage: Optional[float] = Field(None, description="Percentage score of the session")
    is_finished: bool = Field(False, description="Indicates if the session is finished")
    actual_number_of_questions: int = Field(0, description="Current number of questions answered in the session")
    finished_at: Optional[datetime] = Field(None, description="Timestamp when the session was finished")
    status: str = Field("in_progress", description="Status of the session, e.g., 'in_progress', 'completed', 'abandoned'")
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the session was last updated")
    class Settings:
        name="user_sessions"
       
        
