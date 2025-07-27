
from domain.entities.skill import Skill
from domain.repositories.skill_repository import SkillRepository
from ...infrastructure.security import ContextualValidator, ValidationContext
from pydantic import ValidationError

class CreateSkillUseCase:
    def __init__(self, skill_repository: SkillRepository):
        self.skill_repository = skill_repository
        self.validator = ContextualValidator()

    async def execute(self, skill: Skill) -> Skill:
        # Validación contextual antes de crear la skill
        context = ValidationContext(
            operation_type="create_skill",
            entity_type="skill",
            user_id="system",  # Aquí se debería obtener del contexto de autenticación
            entity_data=skill.dict()
        )
        
        validation_result = await self.validator.validate(context)
        if not validation_result.is_valid:
            raise ValidationError(validation_result.errors)
        
        return await self.skill_repository.create_skill(skill)
