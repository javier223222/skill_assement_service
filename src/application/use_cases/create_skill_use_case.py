
from domain.entities.skill import Skill
from domain.repositories.skill_repository import SkillRepository
class CreateSkillUseCase:
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository

    async def execute(self, skill: Skill) -> Skill:
        return await self.skill_repository.create_skill(skill)
