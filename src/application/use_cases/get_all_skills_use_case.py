from domain.entities.skill import Skill
from domain.repositories.skill_repository import SkillRepository
from presentation.schemas.get_all_skill_response_model import GetAllSkillResponseModel
class GetAllSkillsUseCase:
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository

    async def execute(self,skip: int = 0,limit: int = 10) :
        total_skills = await self.skill_repository.count_skills()
        total_pages = (total_skills + limit - 1) // limit
        has_next_page = skip + limit < total_skills
        has_previous_page = skip > 0
        skills = await self.skill_repository.find_all_skills(limit=limit, skip=skip)

        return GetAllSkillResponseModel(
            total_skills=total_skills,
            total_pages=total_pages,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
            current_page=(skip // limit) + 1,
            limit=limit,
            skills=skills
        )