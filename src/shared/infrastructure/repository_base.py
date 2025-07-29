"""
Base Repository Pattern para DDD
Define interfaces y comportamientos comunes
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from shared.domain.base_entity import BaseEntity, AggregateRoot

# Type variables para generics
EntityType = TypeVar('EntityType', bound=BaseEntity)
AggregateType = TypeVar('AggregateType', bound=AggregateRoot)


class IRepository(ABC, Generic[EntityType]):
    """
    Interfaz base para todos los repositorios
    Define operaciones CRUD básicas
    """
    
    @abstractmethod
    async def save(self, entity: EntityType) -> EntityType:
        """Guarda una entidad (crear o actualizar)"""
        pass
    
    @abstractmethod
    async def find_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Busca una entidad por su ID"""
        pass
    
    @abstractmethod
    async def find_all(self, limit: int = 100, offset: int = 0) -> List[EntityType]:
        """Obtiene todas las entidades con paginación"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Elimina una entidad por su ID"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """Verifica si existe una entidad con el ID dado"""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Cuenta el total de entidades"""
        pass


class ISpecification(ABC, Generic[EntityType]):
    """
    Interfaz para implementar el patrón Specification
    Permite encapsular lógica de consulta compleja
    """
    
    @abstractmethod
    def is_satisfied_by(self, entity: EntityType) -> bool:
        """Verifica si una entidad satisface la especificación"""
        pass
    
    @abstractmethod
    def to_query(self) -> Dict[str, Any]:
        """Convierte la especificación a una consulta de base de datos"""
        pass


class IQueryRepository(ABC, Generic[EntityType]):
    """
    Interfaz para repositorios de consulta (CQRS - Query side)
    Optimizado para operaciones de lectura
    """
    
    @abstractmethod
    async def find_by_specification(
        self, 
        specification: ISpecification[EntityType],
        limit: int = 100,
        offset: int = 0
    ) -> List[EntityType]:
        """Busca entidades que satisfagan una especificación"""
        pass
    
    @abstractmethod
    async def find_one_by_specification(
        self, 
        specification: ISpecification[EntityType]
    ) -> Optional[EntityType]:
        """Busca una entidad que satisfaga una especificación"""
        pass
    
    @abstractmethod
    async def count_by_specification(
        self, 
        specification: ISpecification[EntityType]
    ) -> int:
        """Cuenta entidades que satisfagan una especificación"""
        pass


class IAggregateRepository(IRepository[AggregateType], ABC):
    """
    Interfaz específica para repositorios de Aggregates
    Incluye manejo de eventos de dominio y versionado
    """
    
    @abstractmethod
    async def save_with_events(self, aggregate: AggregateType) -> AggregateType:
        """
        Guarda un aggregate y publica sus eventos de dominio
        """
        pass
    
    @abstractmethod
    async def find_by_id_with_version(
        self, 
        aggregate_id: str, 
        expected_version: Optional[int] = None
    ) -> Optional[AggregateType]:
        """
        Busca un aggregate verificando su versión (optimistic locking)
        """
        pass


class IUnitOfWork(ABC):
    """
    Interfaz para el patrón Unit of Work
    Maneja transacciones y consistencia entre aggregates
    """
    
    @abstractmethod
    async def begin(self) -> None:
        """Inicia una transacción"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Confirma la transacción"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Revierte la transacción"""
        pass
    
    @abstractmethod
    async def add_aggregate(self, aggregate: AggregateRoot) -> None:
        """Registra un aggregate para ser persistido"""
        pass
    
    @abstractmethod
    async def get_aggregates(self) -> List[AggregateRoot]:
        """Obtiene todos los aggregates registrados"""
        pass


class BaseRepository(IRepository[EntityType], ABC):
    """
    Implementación base del patrón Repository
    Proporciona funcionalidad común para todos los repositorios
    """
    
    def __init__(self):
        self._entity_cache: Dict[str, EntityType] = {}
        self._cache_enabled: bool = False
    
    def enable_cache(self) -> None:
        """Habilita el cache de entidades"""
        self._cache_enabled = True
    
    def disable_cache(self) -> None:
        """Deshabilita el cache de entidades"""
        self._cache_enabled = False
        self._entity_cache.clear()
    
    def _cache_entity(self, entity: EntityType) -> None:
        """Almacena una entidad en cache"""
        if self._cache_enabled:
            self._entity_cache[entity.id] = entity
    
    def _get_cached_entity(self, entity_id: str) -> Optional[EntityType]:
        """Obtiene una entidad del cache"""
        if self._cache_enabled:
            return self._entity_cache.get(entity_id)
        return None
    
    def _remove_from_cache(self, entity_id: str) -> None:
        """Remueve una entidad del cache"""
        if self._cache_enabled and entity_id in self._entity_cache:
            del self._entity_cache[entity_id]
    
    async def find_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Implementación base que verifica cache primero"""
        # Verificar cache primero
        cached_entity = self._get_cached_entity(entity_id)
        if cached_entity:
            return cached_entity
        
        # Si no está en cache, delegar a implementación específica
        entity = await self._find_by_id_from_storage(entity_id)
        if entity:
            self._cache_entity(entity)
        
        return entity
    
    @abstractmethod
    async def _find_by_id_from_storage(self, entity_id: str) -> Optional[EntityType]:
        """Implementación específica para buscar en el storage"""
        pass
    
    async def save(self, entity: EntityType) -> EntityType:
        """Implementación base que actualiza cache"""
        saved_entity = await self._save_to_storage(entity)
        self._cache_entity(saved_entity)
        return saved_entity
    
    @abstractmethod
    async def _save_to_storage(self, entity: EntityType) -> EntityType:
        """Implementación específica para guardar en el storage"""
        pass
    
    async def delete(self, entity_id: str) -> bool:
        """Implementación base que actualiza cache"""
        result = await self._delete_from_storage(entity_id)
        if result:
            self._remove_from_cache(entity_id)
        return result
    
    @abstractmethod
    async def _delete_from_storage(self, entity_id: str) -> bool:
        """Implementación específica para eliminar del storage"""
        pass
