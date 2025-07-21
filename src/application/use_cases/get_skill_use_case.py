from domain.entities.skill import Skill
from domain.repositories.skill_repository import SkillRepository

class GetSkillUseCase:
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository

    async def execute(self, skill_id: str) -> Skill:
        skill = await self.skill_repository.find_skill_by_id(skill_id)
        if not skill:
            raise ValueError(f"Skill with ID '{skill_id}' not found.")
        return skill