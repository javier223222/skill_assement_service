from pydantic import BaseModel, Field, validator
from infrastructure.security.input_sanitizer import InputSanitizer

class StartAssessmentModel(BaseModel):
    id_user: str = Field(..., description="User ID to start assessment")
    
    @validator('id_user')
    def validate_user_id(cls, v):
        """Valida formato del ID de usuario."""
        return InputSanitizer.validate_id_format(v)
    