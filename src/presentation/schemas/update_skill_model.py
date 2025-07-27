from pydantic import BaseModel, Field, validator
from typing import Optional
from infrastructure.security.input_sanitizer import InputSanitizer

class UpdateSkillModel(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    created_at: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Sanitiza y valida el nombre de la habilidad si está presente."""
        if v is not None:
            return InputSanitizer.sanitize_skill_name(v)
        return v
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitiza y valida la descripción de la habilidad si está presente."""
        if v is not None:
            return InputSanitizer.sanitize_description(v)
        return v
    

    