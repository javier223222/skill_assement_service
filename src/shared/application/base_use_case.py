"""
Base Use Case para Application Layer
Implementa patrones comunes para casos de uso
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

# Type variables
RequestType = TypeVar('RequestType')
ResponseType = TypeVar('ResponseType')


@dataclass
class UseCaseRequest:
    """Base class para todas las requests de casos de uso"""
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class UseCaseResponse:
    """Base class para todas las responses de casos de uso"""
    success: bool
    message: Optional[str] = None
    error_code: Optional[str] = None
    data: Optional[Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class IUseCase(ABC, Generic[RequestType, ResponseType]):
    """
    Interfaz base para todos los casos de uso
    Implementa el patrón Command/Query
    """
    
    @abstractmethod
    async def execute(self, request: RequestType) -> ResponseType:
        """Ejecuta el caso de uso"""
        pass


class BaseUseCase(IUseCase[RequestType, ResponseType], ABC):
    """
    Implementación base para casos de uso
    Proporciona funcionalidad común como logging y validación
    """
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
    
    async def execute(self, request: RequestType) -> ResponseType:
        """
        Template method que incluye logging y manejo de errores
        """
        self._logger.info(f"Executing use case: {self.__class__.__name__}")
        
        try:
            # Validar request
            await self._validate_request(request)
            
            # Ejecutar lógica específica
            response = await self._execute_internal(request)
            
            self._logger.info(f"Use case executed successfully: {self.__class__.__name__}")
            return response
            
        except Exception as e:
            self._logger.error(f"Error executing use case {self.__class__.__name__}: {e}")
            raise
    
    async def _validate_request(self, request: RequestType) -> None:
        """
        Valida el request antes de ejecutar
        Override en subclases si es necesario
        """
        pass
    
    @abstractmethod
    async def _execute_internal(self, request: RequestType) -> ResponseType:
        """Implementación específica del caso de uso"""
        pass


class CommandUseCase(BaseUseCase[RequestType, ResponseType], ABC):
    """
    Base class para casos de uso de tipo Command (CQRS)
    Casos de uso que modifican el estado del sistema
    """
    
    def __init__(self):
        super().__init__()
        self._events_to_publish = []
    
    async def _execute_internal(self, request: RequestType) -> ResponseType:
        """Template method para comandos"""
        # Ejecutar comando
        response = await self._execute_command(request)
        
        # Publicar eventos si los hay
        await self._publish_events()
        
        return response
    
    @abstractmethod
    async def _execute_command(self, request: RequestType) -> ResponseType:
        """Implementación específica del comando"""
        pass
    
    async def _publish_events(self) -> None:
        """Publica eventos de dominio acumulados"""
        from shared.domain.events import domain_event_publisher
        
        for event in self._events_to_publish:
            await domain_event_publisher.publish_event(event)
        
        self._events_to_publish.clear()
    
    def _add_event_to_publish(self, event) -> None:
        """Agrega un evento para ser publicado"""
        self._events_to_publish.append(event)


class QueryUseCase(BaseUseCase[RequestType, ResponseType], ABC):
    """
    Base class para casos de uso de tipo Query (CQRS)
    Casos de uso que solo leen datos sin modificar el estado
    """
    
    async def _execute_internal(self, request: RequestType) -> ResponseType:
        """Template method para queries"""
        return await self._execute_query(request)
    
    @abstractmethod
    async def _execute_query(self, request: RequestType) -> ResponseType:
        """Implementación específica de la consulta"""
        pass


# Request/Response types específicos para comandos comunes
@dataclass
class CreateEntityRequest(UseCaseRequest):
    """Request base para crear entidades"""
    entity_data: Dict[str, Any]


@dataclass
class UpdateEntityRequest(UseCaseRequest):
    """Request base para actualizar entidades"""
    entity_id: str
    entity_data: Dict[str, Any]
    expected_version: Optional[int] = None


@dataclass
class DeleteEntityRequest(UseCaseRequest):
    """Request base para eliminar entidades"""
    entity_id: str


@dataclass
class GetEntityRequest(UseCaseRequest):
    """Request base para obtener entidades"""
    entity_id: str


@dataclass
class GetEntitiesRequest(UseCaseRequest):
    """Request base para obtener múltiples entidades"""
    filters: Optional[Dict[str, Any]] = None
    page: int = 1
    page_size: int = 10
    sort_by: Optional[str] = None
    sort_order: str = "asc"


@dataclass
class EntityResponse(UseCaseResponse):
    """Response base para operaciones con entidades"""
    entity_id: Optional[str] = None
    entity_data: Optional[Dict[str, Any]] = None


@dataclass
class EntitiesResponse(UseCaseResponse):
    """Response base para múltiples entidades"""
    entities: Optional[list] = None
    total_count: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        if self.entities and self.page_size > 0:
            self.total_pages = (self.total_count + self.page_size - 1) // self.page_size
