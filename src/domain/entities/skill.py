from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime,timezone


class Skill(Document):
    name: str = Field(  description="The name of the skill")
    description: Optional[str] = Field(None, description="A brief description of the skill")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(None, description="The last time the skill was updated")
    
    class Settings:
        name="skills"
       

        
       
        
    
   
