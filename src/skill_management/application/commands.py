"""
Commands para Skill Management
Implementa el patrón CQRS - Command side
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from shared.application.base_use_case import UseCaseRequest, UseCaseResponse


@dataclass
class CreateSkillCommand(UseCaseRequest):
    """Comando para crear una nueva skill"""
    name: str
    description: str
    category: str
    difficulty_level: str
    tags: Optional[str] = None


@dataclass
class UpdateSkillCommand(UseCaseRequest):
    """Comando para actualizar una skill existente"""
    skill_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    tags: Optional[str] = None
    expected_version: Optional[int] = None


@dataclass
class ChangeSkillStatusCommand(UseCaseRequest):
    """Comando para cambiar el estado de una skill"""
    skill_id: str
    new_status: str
    expected_version: Optional[int] = None


@dataclass
class DeleteSkillCommand(UseCaseRequest):
    """Comando para eliminar una skill"""
    skill_id: str


@dataclass
class BulkStatusChangeCommand(UseCaseRequest):
    """Comando para cambiar el estado de múltiples skills"""
    skill_ids: list[str]
    new_status: str


# Responses
@dataclass
class SkillCommandResponse(UseCaseResponse):
    """Response base para comandos de skill"""
    skill_id: Optional[str] = None
    skill_data: Optional[Dict[str, Any]] = None


@dataclass
class BulkOperationResponse(UseCaseResponse):
    """Response para operaciones en lote"""
    successful_ids: list[str] = None
    failed_ids: list[str] = None
    errors: list[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.successful_ids is None:
            self.successful_ids = []
        if self.failed_ids is None:
            self.failed_ids = []
        if self.errors is None:
            self.errors = []
