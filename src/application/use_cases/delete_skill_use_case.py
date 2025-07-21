from domain.repositories.skill_repository import SkillRepository
from domain.repositories.question_repository import QuestionRepository

class DeleteSkillUseCase:
    def __init__(self, skill_repository: SkillRepository, question_repository: QuestionRepository):
        self.skill_repository = skill_repository
        self.question_repository = question_repository

    async def execute(self, skill_id: str) -> bool:
        
        skill = await self.skill_repository.find_skill_by_id(skill_id)
        if not skill:
            raise ValueError(f"Skill with ID '{skill_id}' not found.")

        await self.question_repository.delete_many_by_skillid(skill_id)
        return await self.skill_repository.delete_skill_by_id(skill_id)