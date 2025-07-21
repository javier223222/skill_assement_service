from typing import List, Optional
from domain.entities.skill import Skill
from domain.repositories.base_repository import BaseRepository

class SkillRepository(BaseRepository[Skill]):
    def __init__(self):
        super().__init__(Skill)
    async def find_all_skills(self, limit: int = 10, skip: int = 0) -> List[Skill]:
        return await self.find_all(limit, skip)
    async def count_skills(self) -> int:
        return await self.count()
    async def create_skill(self, skill: Skill) -> Skill:
        exiting_skill = await self.find_by_name(skill.name)
        if exiting_skill:
            raise ValueError(f"Skill with name '{skill.name}' already exists.")
        return await self.create(skill)
    async def update_skill(self, skill: Skill) -> Skill:
        
        return await self.update(skill)
        
        
    async def delete_skill_by_id(self, skill_id: str) -> bool:
        return await self.delete_by_id(skill_id)
    async def delete_skill(self, skill: Skill) -> bool:
        return await self.delete(skill)
    async def find_skill_by_id(self, skill_id: str) -> Optional[Skill]:

        return await self.find_by_id(skill_id)
    async def find_by_name(self, name: str) -> Optional[Skill]:
        return await self.model_class.find_one(Skill.name == name)
