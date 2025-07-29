"""
Command Handlers para Skill Management
Implementa los casos de uso del lado Command (CQRS)
"""

from shared.application.base_use_case import CommandUseCase
from shared.domain.exceptions import EntityNotFoundException, ValidationException
from skill_management.domain.skill import Skill
from skill_management.domain.value_objects import (
    SkillName, SkillDescription, SkillCategory, 
    DifficultyLevel, SkillTags, SkillStatus
)
from skill_management.domain.repositories import ISkillRepository
from skill_management.domain.services import SkillDomainService
from skill_management.application.commands import (
    CreateSkillCommand, UpdateSkillCommand, ChangeSkillStatusCommand,
    DeleteSkillCommand, BulkStatusChangeCommand,
    SkillCommandResponse, BulkOperationResponse
)


class CreateSkillHandler(CommandUseCase[CreateSkillCommand, SkillCommandResponse]):
    """Handler para crear nuevas skills"""
    
    def __init__(self, skill_repository: ISkillRepository, skill_domain_service: SkillDomainService):
        super().__init__()
        self._skill_repository = skill_repository
        self._skill_domain_service = skill_domain_service
    
    async def _validate_request(self, request: CreateSkillCommand) -> None:
        """Valida los datos del comando"""
        if not request.name or len(request.name.strip()) < 2:
            raise ValidationException("name", request.name, "Name must be at least 2 characters")
        
        if not request.description or len(request.description.strip()) < 10:
            raise ValidationException("description", request.description, "Description must be at least 10 characters")
    
    async def _execute_command(self, request: CreateSkillCommand) -> SkillCommandResponse:
        """Ejecuta la creación de la skill"""
        try:
            # Crear value objects
            name = SkillName(request.name)
            description = SkillDescription(request.description)
            category = SkillCategory(request.category)
            difficulty = DifficultyLevel(request.difficulty_level)
            tags = SkillTags(request.tags or "")
            
            # Crear la skill
            skill = Skill(
                name=name,
                description=description,
                category=category,
                difficulty_level=difficulty,
                tags=tags
            )
            
            # Validar reglas de dominio
            await self._skill_domain_service.validate_skill_creation(skill)
            
            # Persistir
            saved_skill = await self._skill_repository.save_with_events(skill)
            
            return SkillCommandResponse(
                success=True,
                message="Skill created successfully",
                skill_id=saved_skill.id,
                skill_data=saved_skill.to_dict()
            )
            
        except Exception as e:
            return SkillCommandResponse(
                success=False,
                message=f"Failed to create skill: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class UpdateSkillHandler(CommandUseCase[UpdateSkillCommand, SkillCommandResponse]):
    """Handler para actualizar skills existentes"""
    
    def __init__(self, skill_repository: ISkillRepository, skill_domain_service: SkillDomainService):
        super().__init__()
        self._skill_repository = skill_repository
        self._skill_domain_service = skill_domain_service
    
    async def _execute_command(self, request: UpdateSkillCommand) -> SkillCommandResponse:
        """Ejecuta la actualización de la skill"""
        try:
            # Obtener skill existente
            skill = await self._skill_repository.find_by_id_with_version(
                request.skill_id, 
                request.expected_version
            )
            
            if not skill:
                raise EntityNotFoundException("Skill", request.skill_id)
            
            # Preparar value objects para actualización
            name = SkillName(request.name) if request.name else None
            description = SkillDescription(request.description) if request.description else None
            category = SkillCategory(request.category) if request.category else None
            difficulty = DifficultyLevel(request.difficulty_level) if request.difficulty_level else None
            
            # Validar nombre único si se está cambiando
            if name:
                await self._skill_domain_service.ensure_unique_skill_name(name, skill.id)
            
            # Actualizar información básica
            skill.update_basic_info(name, description, category, difficulty)
            
            # Actualizar tags si se proporcionaron
            if request.tags is not None:
                tags = SkillTags(request.tags)
                skill.update_tags(tags)
            
            # Persistir cambios
            updated_skill = await self._skill_repository.save_with_events(skill)
            
            return SkillCommandResponse(
                success=True,
                message="Skill updated successfully",
                skill_id=updated_skill.id,
                skill_data=updated_skill.to_dict()
            )
            
        except Exception as e:
            return SkillCommandResponse(
                success=False,
                message=f"Failed to update skill: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class ChangeSkillStatusHandler(CommandUseCase[ChangeSkillStatusCommand, SkillCommandResponse]):
    """Handler para cambiar el estado de una skill"""
    
    def __init__(self, skill_repository: ISkillRepository):
        super().__init__()
        self._skill_repository = skill_repository
    
    async def _execute_command(self, request: ChangeSkillStatusCommand) -> SkillCommandResponse:
        """Ejecuta el cambio de estado"""
        try:
            # Obtener skill
            skill = await self._skill_repository.find_by_id_with_version(
                request.skill_id,
                request.expected_version
            )
            
            if not skill:
                raise EntityNotFoundException("Skill", request.skill_id)
            
            # Cambiar estado
            new_status = SkillStatus(request.new_status)
            skill.change_status(new_status)
            
            # Persistir
            updated_skill = await self._skill_repository.save_with_events(skill)
            
            return SkillCommandResponse(
                success=True,
                message=f"Skill status changed to {request.new_status}",
                skill_id=updated_skill.id,
                skill_data=updated_skill.to_dict()
            )
            
        except Exception as e:
            return SkillCommandResponse(
                success=False,
                message=f"Failed to change skill status: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class DeleteSkillHandler(CommandUseCase[DeleteSkillCommand, SkillCommandResponse]):
    """Handler para eliminar skills"""
    
    def __init__(self, skill_repository: ISkillRepository, skill_domain_service: SkillDomainService):
        super().__init__()
        self._skill_repository = skill_repository
        self._skill_domain_service = skill_domain_service
    
    async def _execute_command(self, request: DeleteSkillCommand) -> SkillCommandResponse:
        """Ejecuta la eliminación de la skill"""
        try:
            # Verificar si se puede eliminar
            can_delete, reason = await self._skill_domain_service.can_delete_skill(request.skill_id)
            
            if not can_delete:
                return SkillCommandResponse(
                    success=False,
                    message=reason,
                    error_code="CANNOT_DELETE_SKILL"
                )
            
            # Eliminar
            deleted = await self._skill_repository.delete(request.skill_id)
            
            if not deleted:
                raise EntityNotFoundException("Skill", request.skill_id)
            
            return SkillCommandResponse(
                success=True,
                message="Skill deleted successfully",
                skill_id=request.skill_id
            )
            
        except Exception as e:
            return SkillCommandResponse(
                success=False,
                message=f"Failed to delete skill: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class BulkStatusChangeHandler(CommandUseCase[BulkStatusChangeCommand, BulkOperationResponse]):
    """Handler para cambios de estado en lote"""
    
    def __init__(self, skill_domain_service: SkillDomainService):
        super().__init__()
        self._skill_domain_service = skill_domain_service
    
    async def _execute_command(self, request: BulkStatusChangeCommand) -> BulkOperationResponse:
        """Ejecuta el cambio de estado en lote"""
        try:
            result = await self._skill_domain_service.bulk_status_change(
                request.skill_ids, 
                request.new_status
            )
            
            return BulkOperationResponse(
                success=True,
                message=f"Bulk operation completed: {len(result['successful'])} successful, {len(result['failed'])} failed",
                successful_ids=result['successful'],
                failed_ids=result['failed'],
                errors=result['errors']
            )
            
        except Exception as e:
            return BulkOperationResponse(
                success=False,
                message=f"Bulk operation failed: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )
