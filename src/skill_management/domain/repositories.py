"""
Repository interface para Skill domain
Define el contrato para la persistencia de Skills
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from shared.infrastructure.repository_base import IAggregateRepository, IQueryRepository
from skill_management.domain.skill import Skill
from skill_management.domain.value_objects import SkillName, SkillCategory, SkillStatus


class ISkillRepository(IAggregateRepository[Skill], ABC):
    """
    Interfaz del repositorio para Skills
    Define todas las operaciones de persistencia específicas del dominio
    """
    
    @abstractmethod
    async def find_by_name(self, name: SkillName) -> Optional[Skill]:
        """Busca una skill por su nombre"""
        pass
    
    @abstractmethod
    async def find_by_category(self, category: SkillCategory) -> List[Skill]:
        """Busca skills por categoría"""
        pass
    
    @abstractmethod
    async def find_by_status(self, status: SkillStatus) -> List[Skill]:
        """Busca skills por estado"""
        pass
    
    @abstractmethod
    async def find_active_skills(self) -> List[Skill]:
        """Obtiene todas las skills activas"""
        pass
    
    @abstractmethod
    async def find_skills_for_assessment(self) -> List[Skill]:
        """Obtiene skills disponibles para evaluación"""
        pass
    
    @abstractmethod
    async def exists_with_name(self, name: SkillName, exclude_id: Optional[str] = None) -> bool:
        """Verifica si existe una skill con el nombre dado"""
        pass
    
    @abstractmethod
    async def find_popular_skills(self, limit: int = 10) -> List[Skill]:
        """Obtiene las skills más populares basadas en uso"""
        pass
    
    @abstractmethod
    async def find_skills_by_difficulty(self, difficulty: str) -> List[Skill]:
        """Busca skills por nivel de dificultad"""
        pass


class ISkillQueryRepository(IQueryRepository[Skill], ABC):
    """
    Interfaz para consultas optimizadas de Skills (CQRS - Query side)
    """
    
    @abstractmethod
    async def get_skill_statistics(self) -> dict:
        """Obtiene estadísticas generales de skills"""
        pass
    
    @abstractmethod
    async def get_skills_summary(
        self, 
        category: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> dict:
        """Obtiene un resumen paginado de skills"""
        pass
    
    @abstractmethod
    async def search_skills(
        self, 
        query: str,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[dict]:
        """Busca skills por texto (nombre, descripción, tags)"""
        pass
