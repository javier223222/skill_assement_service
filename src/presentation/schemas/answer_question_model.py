from pydantic import BaseModel, Field, validator, root_validator
from infrastructure.security.input_sanitizer import InputSanitizer

class AnswerModel(BaseModel):
    id_session: str = Field(..., description="Session ID")
    id_user: str = Field(..., description="User ID")
    
    @validator('id_session', 'id_user')
    def validate_ids(cls, v):
        """Valida formato de IDs."""
        return InputSanitizer.validate_id_format(v)

class AnswerQuestionModel(AnswerModel):
    answer: str = Field(..., min_length=1, max_length=2000, description="User answer")
    
    @validator('answer')
    def validate_answer(cls, v):
        """Sanitiza y valida la respuesta del usuario."""
        return InputSanitizer.sanitize_answer(v)
    
    @root_validator
    def validate_session_context(cls, values):
        """Validaciones cruzadas para contexto de sesión."""
        id_session = values.get('id_session')
        id_user = values.get('id_user')
        
        if id_session and id_user:
            # Validar que los IDs no estén vacíos después de sanitización
            if not id_session.strip() or not id_user.strip():
                raise ValueError("Session ID and User ID cannot be empty")
        
        return values