
from pydantic import BaseModel
class AnswerQuestionBaseDto(BaseModel):
   id_question:int
   id_session:str
   id_user:str

class AnswerQuestionDTO(AnswerQuestionBaseDto):

   answer:str
