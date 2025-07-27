from beanie import Document
from pydantic import Field, validator
from typing import List, Optional
from datetime import datetime, timezone
from infrastructure.security.input_sanitizer import InputSanitizer


class Question(Document):
    id: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp()), index=True, description="Unique identifier for the question")
    skillid: str = Field(..., index=True, description="The ID of the skill associated with the question")
    subcategory: str = Field(..., index=True, max_length=200, description="The subcategory of the question")
    type: str = Field(..., max_length=50, description="The type of the question (e.g., multiple choice)")
    question: str = Field(..., min_length=10, max_length=1000, description="The text of the question")
    options: List[str] = Field(..., description="List of options for the question")
    correct_answer: str = Field(..., max_length=500, description="The correct answer to the question")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the question was created")
    updated_at: Optional[datetime] = Field(default=None, description="Timestamp when the question was last updated")
    recommended_tools: Optional[List[str]] = Field(default=None, description="List of recommended tools related to the question")
    
    @validator('skillid')
    def validate_skill_id(cls, v):
        """Valida formato del skill ID."""
        return InputSanitizer.validate_id_format(v)
    
    @validator('subcategory', 'type')
    def validate_text_fields(cls, v):
        """Sanitiza campos de texto básicos."""
        return InputSanitizer.sanitize_text(v, max_length=200)
    
    @validator('question')
    def validate_question_text(cls, v):
        """Sanitiza el texto de la pregunta."""
        return InputSanitizer.sanitize_text(v, max_length=1000, allow_special_chars=True)
    
    @validator('options')
    def validate_options(cls, v):
        """Valida y sanitiza las opciones de respuesta."""
        if not v or len(v) < 2:
            raise ValueError("At least 2 options are required")
        
        if len(v) > 6:
            raise ValueError("Maximum 6 options allowed")
        
        sanitized_options = []
        for option in v:
            if not isinstance(option, str):
                raise ValueError("All options must be strings")
            sanitized_option = InputSanitizer.sanitize_text(option, max_length=500, allow_special_chars=True)
            sanitized_options.append(sanitized_option)
        
        return sanitized_options
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v):
        """Sanitiza la respuesta correcta."""
        return InputSanitizer.sanitize_text(v, max_length=500, allow_special_chars=True)
    
    @validator('recommended_tools')
    def validate_recommended_tools(cls, v):
        """Valida y sanitiza herramientas recomendadas."""
        if v is not None:
            sanitized_tools = []
            for tool in v:
                if not isinstance(tool, str):
                    raise ValueError("All tools must be strings")
                sanitized_tool = InputSanitizer.sanitize_text(tool, max_length=100)
                sanitized_tools.append(sanitized_tool)
            return sanitized_tools
        return v
    
    class Settings:
        collection = "questions"
        indexes = [
            [("skillid", 1)],
            [("subcategory", 1)],
            [("type", 1)],
            [("question", 1)]
        ]




    
    
  
        

