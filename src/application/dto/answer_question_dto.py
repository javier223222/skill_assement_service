
from pydantic import BaseModel, Field, validator, root_validator
from infrastructure.security.input_sanitizer import InputSanitizer

class AnswerQuestionBaseDto(BaseModel):
   id_question: int = Field(..., ge=1, description="Question ID")
   id_session: str = Field(..., description="Session ID")
   id_user: str = Field(..., description="User ID")
   
   @validator('id_session', 'id_user')
   def validate_ids(cls, v):
       """Valida formato de IDs."""
       return InputSanitizer.validate_id_format(v)
   
   @root_validator
   def validate_question_context(cls, values):
       """Validaciones cruzadas para contexto de pregunta."""
       id_question = values.get('id_question')
       id_session = values.get('id_session')
       
       if id_question is not None and id_question <= 0:
           raise ValueError("Question ID must be positive")
       
       return values

class AnswerQuestionDTO(AnswerQuestionBaseDto):
   answer: str = Field(..., min_length=1, max_length=2000, description="User answer")
   
   @validator('answer')
   def validate_answer(cls, v):
       """Sanitiza y valida la respuesta del usuario."""
       return InputSanitizer.sanitize_answer(v)
