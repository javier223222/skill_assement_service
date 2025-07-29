"""
Queries para Skill Management
Implementa el patrón CQRS - Query side
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from shared.application.base_use_case import UseCaseRequest, UseCaseResponse


@dataclass
class GetSkillByIdQuery(UseCaseRequest):
    """Query para obtener una skill por ID"""
    skill_id: str


@dataclass
class GetAllSkillsQuery(UseCaseRequest):
    """Query para obtener todas las skills con filtros opcionales"""
    category: Optional[str] = None
    status: Optional[str] = None
    difficulty: Optional[str] = None
    page: int = 1
    page_size: int = 10
    sort_by: Optional[str] = None
    sort_order: str = "asc"


@dataclass
class SearchSkillsQuery(UseCaseRequest):
    """Query para buscar skills por texto"""
    search_text: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    limit: int = 10


@dataclass
class GetSkillsByCategoryQuery(UseCaseRequest):
    """Query para obtener skills por categoría"""
    category: str
    include_inactive: bool = False


@dataclass
class GetPopularSkillsQuery(UseCaseRequest):
    """Query para obtener skills populares"""
    limit: int = 10
    category: Optional[str] = None


@dataclass
class GetSkillStatisticsQuery(UseCaseRequest):
    """Query para obtener estadísticas de skills"""
    pass


@dataclass
class GetSkillProgressionQuery(UseCaseRequest):
    """Query para obtener ruta de progresión de una skill"""
    skill_id: str


@dataclass
class GetCategoryCoverageQuery(UseCaseRequest):
    """Query para obtener cobertura por categorías"""
    pass


# Responses
@dataclass
class SkillQueryResponse(UseCaseResponse):
    """Response para consultas de una sola skill"""
    skill: Optional[Dict[str, Any]] = None


@dataclass
class SkillsQueryResponse(UseCaseResponse):
    """Response para consultas de múltiples skills"""
    skills: List[Dict[str, Any]] = None
    total_count: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0
    
    def __post_init__(self):
        super().__post_init__()
        if self.skills is None:
            self.skills = []
        if self.page_size > 0:
            self.total_pages = (self.total_count + self.page_size - 1) // self.page_size


@dataclass
class SkillStatisticsResponse(UseCaseResponse):
    """Response para estadísticas de skills"""
    statistics: Optional[Dict[str, Any]] = None


@dataclass
class CategoryCoverageResponse(UseCaseResponse):
    """Response para cobertura de categorías"""
    coverage: Optional[Dict[str, Any]] = None
