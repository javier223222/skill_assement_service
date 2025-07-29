"""
Skill Entity refactorizada siguiendo DDD
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from shared.domain.base_entity import AggregateRoot, DomainEvent
from shared.domain.exceptions import ValidationException, BusinessRuleException
from skill_management.domain.value_objects import (
    SkillName, SkillDescription, DifficultyLevel, 
    SkillCategory, SkillTags, SkillStatus
)


class SkillCreatedEvent(DomainEvent):
    """Evento que se dispara cuando se crea una nueva skill"""
    
    def __init__(self, skill_id: str, skill_name: str, category: str):
        super().__init__(
            event_type="SkillCreated",
            aggregate_id=skill_id,
            event_data={
                "skill_name": skill_name,
                "category": category,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        )


class SkillUpdatedEvent(DomainEvent):
    """Evento que se dispara cuando se actualiza una skill"""
    
    def __init__(self, skill_id: str, changed_fields: Dict[str, Any]):
        super().__init__(
            event_type="SkillUpdated",
            aggregate_id=skill_id,
            event_data={
                "changed_fields": changed_fields,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        )


class SkillStatusChangedEvent(DomainEvent):
    """Evento que se dispara cuando cambia el estado de una skill"""
    
    def __init__(self, skill_id: str, old_status: str, new_status: str):
        super().__init__(
            event_type="SkillStatusChanged",
            aggregate_id=skill_id,
            event_data={
                "old_status": old_status,
                "new_status": new_status,
                "changed_at": datetime.now(timezone.utc).isoformat()
            }
        )


class Skill(AggregateRoot):
    """
    Aggregate Root para el dominio de Skills
    Encapsula todas las reglas de negocio relacionadas con skills
    """
    
    def __init__(
        self,
        name: SkillName,
        description: SkillDescription,
        category: SkillCategory,
        difficulty_level: DifficultyLevel,
        skill_id: Optional[str] = None,
        tags: Optional[SkillTags] = None,
        status: Optional[SkillStatus] = None
    ):
        super().__init__(skill_id)
        
        # Value Objects
        self._name = name
        self._description = description
        self._category = category
        self._difficulty_level = difficulty_level
        self._tags = tags or SkillTags("")
        self._status = status or SkillStatus(SkillStatus.DRAFT)
        
        # Business metrics
        self._total_assessments = 0
        self._average_score = 0.0
        self._times_used = 0
        
        # Add creation event
        if skill_id is None:  # New skill
            self.add_domain_event(
                SkillCreatedEvent(self.id, self._name.value, self._category.value)
            )
    
    # Properties (read-only access to value objects)
    @property
    def name(self) -> SkillName:
        return self._name
    
    @property
    def description(self) -> SkillDescription:
        return self._description
    
    @property
    def category(self) -> SkillCategory:
        return self._category
    
    @property
    def difficulty_level(self) -> DifficultyLevel:
        return self._difficulty_level
    
    @property
    def tags(self) -> SkillTags:
        return self._tags
    
    @property
    def status(self) -> SkillStatus:
        return self._status
    
    @property
    def total_assessments(self) -> int:
        return self._total_assessments
    
    @property
    def average_score(self) -> float:
        return self._average_score
    
    @property
    def times_used(self) -> int:
        return self._times_used
    
    # Business methods
    def update_basic_info(
        self,
        name: Optional[SkillName] = None,
        description: Optional[SkillDescription] = None,
        category: Optional[SkillCategory] = None,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> None:
        """
        Actualiza información básica de la skill
        Valida reglas de negocio antes de aplicar cambios
        """
        # Business rule: No se puede modificar skills archivadas
        if self._status.value == SkillStatus.ARCHIVED:
            raise BusinessRuleException(
                "Cannot modify archived skills",
                {"skill_id": self.id, "current_status": self._status.value}
            )
        
        changed_fields = {}
        
        if name and name.value != self._name.value:
            # Business rule: Validar unicidad del nombre (se delega al dominio service)
            self._name = name
            changed_fields["name"] = name.value
        
        if description and description.value != self._description.value:
            self._description = description
            changed_fields["description"] = description.value
        
        if category and category.value != self._category.value:
            self._category = category
            changed_fields["category"] = category.value
        
        if difficulty_level and difficulty_level.value != self._difficulty_level.value:
            self._difficulty_level = difficulty_level
            changed_fields["difficulty_level"] = difficulty_level.value
        
        if changed_fields:
            self.mark_as_updated()
            self.increment_version()
            self.add_domain_event(
                SkillUpdatedEvent(self.id, changed_fields)
            )
    
    def update_tags(self, tags: SkillTags) -> None:
        """Actualiza los tags de la skill"""
        if self._status.value == SkillStatus.ARCHIVED:
            raise BusinessRuleException(
                "Cannot modify archived skills",
                {"skill_id": self.id}
            )
        
        if tags.value != self._tags.value:
            old_tags = self._tags.value
            self._tags = tags
            
            self.mark_as_updated()
            self.add_domain_event(
                SkillUpdatedEvent(self.id, {
                    "tags": {"old": old_tags, "new": tags.value}
                })
            )
    
    def change_status(self, new_status: SkillStatus) -> None:
        """
        Cambia el estado de la skill
        Valida transiciones válidas
        """
        if not self._status.can_transition_to(new_status):
            raise BusinessRuleException(
                f"Invalid status transition from {self._status.value} to {new_status.value}",
                {
                    "skill_id": self.id,
                    "current_status": self._status.value,
                    "requested_status": new_status.value
                }
            )
        
        old_status = self._status.value
        self._status = new_status
        
        self.mark_as_updated()
        self.increment_version()
        self.add_domain_event(
            SkillStatusChangedEvent(self.id, old_status, new_status.value)
        )
    
    def activate(self) -> None:
        """Activa la skill para uso en evaluaciones"""
        self.change_status(SkillStatus(SkillStatus.ACTIVE))
    
    def deactivate(self) -> None:
        """Desactiva la skill"""
        self.change_status(SkillStatus(SkillStatus.INACTIVE))
    
    def archive(self) -> None:
        """Archiva la skill (operación irreversible)"""
        self.change_status(SkillStatus(SkillStatus.ARCHIVED))
    
    def can_be_used_for_assessment(self) -> bool:
        """Verifica si la skill puede ser usada en evaluaciones"""
        return self._status.is_available_for_assessment()
    
    def record_assessment_usage(self, score: float) -> None:
        """
        Registra el uso de la skill en una evaluación
        Actualiza métricas internas
        """
        if not self.can_be_used_for_assessment():
            raise BusinessRuleException(
                "Cannot use inactive skill for assessment",
                {"skill_id": self.id, "status": self._status.value}
            )
        
        if not 0 <= score <= 100:
            raise ValidationException("score", score, "Score must be between 0 and 100")
        
        # Actualizar métricas
        total_score = (self._average_score * self._total_assessments) + score
        self._total_assessments += 1
        self._average_score = total_score / self._total_assessments
        self._times_used += 1
        
        self.mark_as_updated()
    
    def get_popularity_score(self) -> float:
        """
        Calcula un score de popularidad basado en uso y calificaciones
        """
        if self._total_assessments == 0:
            return 0.0
        
        # Fórmula simple: (promedio_score * log(total_evaluaciones + 1)) / 10
        import math
        return (self._average_score * math.log(self._total_assessments + 1)) / 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la skill a diccionario para persistencia"""
        return {
            "_id": self.id,
            "name": self._name.value,
            "description": self._description.value,
            "category": self._category.value,
            "difficulty_level": self._difficulty_level.value,
            "tags": self._tags.value,
            "status": self._status.value,
            "total_assessments": self._total_assessments,
            "average_score": self._average_score,
            "times_used": self._times_used,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        """Crea una skill desde un diccionario (para hidratación desde DB)"""
        skill = cls(
            skill_id=data.get("_id"),
            name=SkillName(data["name"]),
            description=SkillDescription(data["description"]),
            category=SkillCategory(data["category"]),
            difficulty_level=DifficultyLevel(data["difficulty_level"]),
            tags=SkillTags(data.get("tags", "")),
            status=SkillStatus(data.get("status", SkillStatus.DRAFT))
        )
        
        # Restaurar métricas
        skill._total_assessments = data.get("total_assessments", 0)
        skill._average_score = data.get("average_score", 0.0)
        skill._times_used = data.get("times_used", 0)
        skill._version = data.get("version", 1)
        
        # Restaurar timestamps
        if "updated_at" in data:
            skill._updated_at = data["updated_at"]
        
        # Limpiar eventos (no queremos replicar eventos de hidratación)
        skill.clear_domain_events()
        
        return skill
    
    def __str__(self) -> str:
        return f"Skill(id={self.id}, name={self._name.value}, category={self._category.value})"
