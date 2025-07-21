from pydantic import BaseModel

class CreateSkillModel(BaseModel):
    name:str
    description: str 
    
    