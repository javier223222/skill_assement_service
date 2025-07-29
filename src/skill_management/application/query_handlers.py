"""
Query Handlers para Skill Management
Implementa los casos de uso del lado Query (CQRS)
"""

from typing import Dict, Any, List
from shared.application.base_use_case import QueryUseCase
from shared.domain.exceptions import EntityNotFoundException
from skill_management.domain.repositories import ISkillRepository, ISkillQueryRepository
from skill_management.domain.services import SkillDomainService
from skill_management.domain.value_objects import SkillCategory
from skill_management.application.queries import (
    GetSkillByIdQuery, GetAllSkillsQuery, SearchSkillsQuery,
    GetSkillsByCategoryQuery, GetPopularSkillsQuery, GetSkillStatisticsQuery,
    GetSkillProgressionQuery, GetCategoryCoverageQuery,
    SkillQueryResponse, SkillsQueryResponse, SkillStatisticsResponse,
    CategoryCoverageResponse
)


class GetSkillByIdHandler(QueryUseCase[GetSkillByIdQuery, SkillQueryResponse]):
    """Handler para obtener una skill por ID"""
    
    def __init__(self, skill_repository: ISkillRepository):
        super().__init__()
        self._skill_repository = skill_repository
    
    async def _execute_query(self, request: GetSkillByIdQuery) -> SkillQueryResponse:
        """Ejecuta la consulta de skill por ID"""
        skill = await self._skill_repository.find_by_id(request.skill_id)
        
        if not skill:
            return SkillQueryResponse(
                success=False,
                message="Skill not found",
                error_code="SKILL_NOT_FOUND"
            )
        
        return SkillQueryResponse(
            success=True,
            message="Skill retrieved successfully",
            skill=skill.to_dict()
        )


class GetAllSkillsHandler(QueryUseCase[GetAllSkillsQuery, SkillsQueryResponse]):
    """Handler para obtener todas las skills con filtros"""
    
    def __init__(self, skill_query_repository: ISkillQueryRepository):
        super().__init__()
        self._skill_query_repository = skill_query_repository
    
    async def _execute_query(self, request: GetAllSkillsQuery) -> SkillsQueryResponse:
        """Ejecuta la consulta de todas las skills"""
        try:
            result = await self._skill_query_repository.get_skills_summary(
                category=request.category,
                status=request.status,
                page=request.page,
                page_size=request.page_size
            )
            
            return SkillsQueryResponse(
                success=True,
                message="Skills retrieved successfully",
                skills=result.get('skills', []),
                total_count=result.get('total_count', 0),
                page=request.page,
                page_size=request.page_size
            )
            
        except Exception as e:
            return SkillsQueryResponse(
                success=False,
                message=f"Failed to retrieve skills: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class SearchSkillsHandler(QueryUseCase[SearchSkillsQuery, SkillsQueryResponse]):
    """Handler para buscar skills por texto"""
    
    def __init__(self, skill_query_repository: ISkillQueryRepository):
        super().__init__()
        self._skill_query_repository = skill_query_repository
    
    async def _execute_query(self, request: SearchSkillsQuery) -> SkillsQueryResponse:
        """Ejecuta la búsqueda de skills"""
        try:
            skills = await self._skill_query_repository.search_skills(
                query=request.search_text,
                category=request.category,
                difficulty=request.difficulty,
                limit=request.limit
            )
            
            return SkillsQueryResponse(
                success=True,
                message="Skills search completed",
                skills=skills,
                total_count=len(skills)
            )
            
        except Exception as e:
            return SkillsQueryResponse(
                success=False,
                message=f"Search failed: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class GetSkillsByCategoryHandler(QueryUseCase[GetSkillsByCategoryQuery, SkillsQueryResponse]):
    """Handler para obtener skills por categoría"""
    
    def __init__(self, skill_repository: ISkillRepository):
        super().__init__()
        self._skill_repository = skill_repository
    
    async def _execute_query(self, request: GetSkillsByCategoryQuery) -> SkillsQueryResponse:
        """Ejecuta la consulta por categoría"""
        try:
            category = SkillCategory(request.category)
            skills = await self._skill_repository.find_by_category(category)
            
            # Filtrar inactivas si no se requieren
            if not request.include_inactive:
                skills = [skill for skill in skills if skill.can_be_used_for_assessment()]
            
            skills_data = [skill.to_dict() for skill in skills]
            
            return SkillsQueryResponse(
                success=True,
                message=f"Skills for category '{request.category}' retrieved successfully",
                skills=skills_data,
                total_count=len(skills_data)
            )
            
        except Exception as e:
            return SkillsQueryResponse(
                success=False,
                message=f"Failed to retrieve skills by category: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class GetPopularSkillsHandler(QueryUseCase[GetPopularSkillsQuery, SkillsQueryResponse]):
    """Handler para obtener skills populares"""
    
    def __init__(self, skill_repository: ISkillRepository):
        super().__init__()
        self._skill_repository = skill_repository
    
    async def _execute_query(self, request: GetPopularSkillsQuery) -> SkillsQueryResponse:
        """Ejecuta la consulta de skills populares"""
        try:
            skills = await self._skill_repository.find_popular_skills(request.limit)
            
            # Filtrar por categoría si se especifica
            if request.category:
                category = SkillCategory(request.category)
                skills = [skill for skill in skills if skill.category.value == category.value]
            
            skills_data = [skill.to_dict() for skill in skills]
            
            return SkillsQueryResponse(
                success=True,
                message="Popular skills retrieved successfully",
                skills=skills_data,
                total_count=len(skills_data)
            )
            
        except Exception as e:
            return SkillsQueryResponse(
                success=False,
                message=f"Failed to retrieve popular skills: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class GetSkillStatisticsHandler(QueryUseCase[GetSkillStatisticsQuery, SkillStatisticsResponse]):
    """Handler para obtener estadísticas de skills"""
    
    def __init__(self, skill_query_repository: ISkillQueryRepository):
        super().__init__()
        self._skill_query_repository = skill_query_repository
    
    async def _execute_query(self, request: GetSkillStatisticsQuery) -> SkillStatisticsResponse:
        """Ejecuta la consulta de estadísticas"""
        try:
            statistics = await self._skill_query_repository.get_skill_statistics()
            
            return SkillStatisticsResponse(
                success=True,
                message="Statistics retrieved successfully",
                statistics=statistics
            )
            
        except Exception as e:
            return SkillStatisticsResponse(
                success=False,
                message=f"Failed to retrieve statistics: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class GetSkillProgressionHandler(QueryUseCase[GetSkillProgressionQuery, SkillsQueryResponse]):
    """Handler para obtener ruta de progresión de una skill"""
    
    def __init__(self, skill_repository: ISkillRepository, skill_domain_service: SkillDomainService):
        super().__init__()
        self._skill_repository = skill_repository
        self._skill_domain_service = skill_domain_service
    
    async def _execute_query(self, request: GetSkillProgressionQuery) -> SkillsQueryResponse:
        """Ejecuta la consulta de progresión"""
        try:
            skill = await self._skill_repository.find_by_id(request.skill_id)
            if not skill:
                return SkillsQueryResponse(
                    success=False,
                    message="Skill not found",
                    error_code="SKILL_NOT_FOUND"
                )
            
            progression_skills = await self._skill_domain_service.get_skill_progression_path(skill)
            skills_data = [skill.to_dict() for skill in progression_skills]
            
            return SkillsQueryResponse(
                success=True,
                message="Skill progression path retrieved successfully",
                skills=skills_data,
                total_count=len(skills_data)
            )
            
        except Exception as e:
            return SkillsQueryResponse(
                success=False,
                message=f"Failed to retrieve skill progression: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )


class GetCategoryCoverageHandler(QueryUseCase[GetCategoryCoverageQuery, CategoryCoverageResponse]):
    """Handler para obtener cobertura de categorías"""
    
    def __init__(self, skill_domain_service: SkillDomainService):
        super().__init__()
        self._skill_domain_service = skill_domain_service
    
    async def _execute_query(self, request: GetCategoryCoverageQuery) -> CategoryCoverageResponse:
        """Ejecuta la consulta de cobertura"""
        try:
            coverage = await self._skill_domain_service.calculate_category_coverage()
            
            return CategoryCoverageResponse(
                success=True,
                message="Category coverage retrieved successfully",
                coverage=coverage
            )
            
        except Exception as e:
            return CategoryCoverageResponse(
                success=False,
                message=f"Failed to retrieve category coverage: {str(e)}",
                error_code=e.__class__.__name__ if hasattr(e, '__class__') else "UNKNOWN_ERROR"
            )
