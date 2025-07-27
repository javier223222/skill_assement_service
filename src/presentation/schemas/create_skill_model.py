from pydantic import BaseModel, Field, validator
from infrastructure.security.input_sanitizer import InputSanitizer

class CreateSkillModel(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Skill name")
    description: str = Field(..., min_length=10, max_length=500, description="Skill description")
    
    @validator('name')
    def validate_name(cls, v):
        """Sanitiza y valida el nombre de la habilidad."""
        return InputSanitizer.sanitize_skill_name(v)
    
    @validator('description')
    def validate_description(cls, v):
        """Sanitiza y valida la descripción de la habilidad."""
        return InputSanitizer.sanitize_description(v)
    
    