from pydantic import BaseModel
class AnswerModel(BaseModel):
    id_session: str
    id_user: str
class AnswerQuestionModel(AnswerModel):
    answer:str