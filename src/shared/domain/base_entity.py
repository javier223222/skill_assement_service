"""
Base Entity para todos los dominios
Implementa conceptos fundamentales de DDD
"""

from abc import ABC
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Base class para todos los eventos de dominio"""
    event_id: str = Field(default_factory=lambda: str(ObjectId()))
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str
    aggregate_id: str
    event_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class BaseEntity(ABC):
    """
    Entidad base que implementa patrones fundamentales de DDD
    - Identity
    - Domain Events
    - Equality
    """
    
    def __init__(self, entity_id: Optional[str] = None):
        self._id: str = entity_id or str(ObjectId())
        self._domain_events: List[DomainEvent] = []
        self._created_at: datetime = datetime.now(timezone.utc)
        self._updated_at: Optional[datetime] = None
    
    @property
    def id(self) -> str:
        """Identificador único de la entidad"""
        return self._id
    
    @property
    def created_at(self) -> datetime:
        """Fecha de creación de la entidad"""
        return self._created_at
    
    @property
    def updated_at(self) -> Optional[datetime]:
        """Fecha de última actualización"""
        return self._updated_at
    
    def mark_as_updated(self) -> None:
        """Marca la entidad como actualizada"""
        self._updated_at = datetime.now(timezone.utc)
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Agrega un evento de dominio a la entidad"""
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> None:
        """Limpia todos los eventos de dominio"""
        self._domain_events.clear()
    
    def get_domain_events(self) -> List[DomainEvent]:
        """Obtiene todos los eventos de dominio"""
        return self._domain_events.copy()
    
    def __eq__(self, other: object) -> bool:
        """Igualdad basada en identidad"""
        if not isinstance(other, BaseEntity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash basado en identidad"""
        return hash(self._id)
    
    def __str__(self) -> str:
        """Representación string de la entidad"""
        return f"{self.__class__.__name__}(id={self._id})"
    
    def __repr__(self) -> str:
        """Representación para debugging"""
        return self.__str__()


class AggregateRoot(BaseEntity):
    """
    Aggregate Root que extiende BaseEntity con capacidades adicionales
    - Manejo de invariantes del agregado
    - Control de acceso a entidades hijas
    """
    
    def __init__(self, aggregate_id: Optional[str] = None):
        super().__init__(aggregate_id)
        self._version: int = 1
    
    @property
    def version(self) -> int:
        """Versión del agregado para optimistic locking"""
        return self._version
    
    def increment_version(self) -> None:
        """Incrementa la versión del agregado"""
        self._version += 1
        self.mark_as_updated()
    
    def publish_domain_events(self) -> List[DomainEvent]:
        """
        Publica y limpia los eventos de dominio
        Retorna los eventos para ser procesados por el EventDispatcher
        """
        events = self.get_domain_events()
        self.clear_domain_events()
        return events
