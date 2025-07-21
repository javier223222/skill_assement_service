from pydantic import BaseModel
from typing import List
from domain.entities.skill import Skill
class GetAllSkillResponseModel(BaseModel):
    total_skills: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool
    current_page: int
    limit: int
    skills: list[Skill]

    