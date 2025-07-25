from pydantic import BaseModel
from typing import Optional
class UpdateSkillModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    

    