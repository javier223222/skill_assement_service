from beanie import Document
from pydantic import Field, validator
from typing import Optional
from datetime import datetime, timezone
from infrastructure.security.input_sanitizer import InputSanitizer


class Skill(Document):
    name: str = Field(..., min_length=3, max_length=100, description="The name of the skill")
    description: Optional[str] = Field(None, max_length=500, description="A brief description of the skill")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(None, description="The last time the skill was updated")
    
    @validator('name')
    def validate_name(cls, v):
        """Sanitiza y valida el nombre de la habilidad."""
        if v is not None:
            return InputSanitizer.sanitize_skill_name(v)
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitiza y valida la descripción de la habilidad."""
        if v is not None:
            return InputSanitizer.sanitize_description(v)
        return v
    
    class Settings:
        name="skills"
       

        
       
        
    
   
