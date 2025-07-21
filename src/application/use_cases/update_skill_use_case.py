from domain.repositories.skill_repository import SkillRepository
from domain.entities.skill import Skill

class UpdateSkillUseCase:
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository

    async def execute(self, skill_data: Skill) -> Skill:
        existing_skill = await self.skill_repository.find_skill_by_id(skill_data.id)
        if not existing_skill:
            raise ValueError(f"Skill with ID '{skill_data.id}' not found.")

        updated_skill = await self.skill_repository.update_skill(skill_data)
        return updated_skill
    