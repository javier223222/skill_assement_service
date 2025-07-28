from beanie import Document
from pydantic import Field
from typing import List,Optional
from datetime import datetime,timezone



class Question(Document):
    question_number: int = Field(..., index=True, description="Sequential number of the question (1, 2, 3, etc.)")
    skillid:str= Field( index=True, description="The ID of the skill associated with the question")
    subcategory: str = Field(..., index=True, description="The subcategory of the question")
    type: str = Field(..., description="The type of the question (e.g., multiple choice)")
    question: str = Field(..., description="The text of the question")
    options: List[str] = Field(..., description="List of options for the question")
    correct_answer: str = Field(..., description="The correct answer to the question")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the question was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the question was last updated")
    recommended_tools: Optional[List[str]] = Field(default=None, description="List of recommended tools related to the question")
    class Settings:
        collection = "questions"
        indexes = [
            [("skillid", 1), ("question_number", 1)],  # Índice compuesto para skillid + question_number
            [("subcategory", 1)],
            [("type", 1)],
            [("question", 1)]
        ]




    
    
  
        

