"""
Domain Services para Skill Management
Implementa lógica de dominio que no pertenece a ninguna entidad específica
"""

from typing import List, Optional
from shared.domain.exceptions import BusinessRuleException, DuplicateEntityException
from skill_management.domain.skill import Skill
from skill_management.domain.value_objects import SkillName, SkillCategory
from skill_management.domain.repositories import ISkillRepository


class SkillDomainService:
    """
    Servicio de dominio para Skills
    Contiene lógica de negocio que involucra múltiples entidades o agregados
    """
    
    def __init__(self, skill_repository: ISkillRepository):
        self._skill_repository = skill_repository
    
    async def ensure_unique_skill_name(self, name: SkillName, exclude_skill_id: Optional[str] = None) -> None:
        """
        Garantiza que el nombre de la skill sea único
        Business Rule: No pueden existir dos skills con el mismo nombre
        """
        exists = await self._skill_repository.exists_with_name(name, exclude_skill_id)
        if exists:
            raise DuplicateEntityException("Skill", "name", name.value)
    
    async def validate_skill_creation(self, skill: Skill) -> None:
        """
        Valida todas las reglas de negocio para la creación de una skill
        """
        # Validar nombre único
        await self.ensure_unique_skill_name(skill.name)
        
        # Aquí se podrían agregar más validaciones:
        # - Límite de skills por categoría
        # - Validaciones específicas por rol de usuario
        # - etc.
    
    async def can_delete_skill(self, skill_id: str) -> tuple[bool, str]:
        """
        Determina si una skill puede ser eliminada
        Business Rule: No se pueden eliminar skills que han sido usadas en evaluaciones
        """
        skill = await self._skill_repository.find_by_id(skill_id)
        if not skill:
            return False, "Skill not found"
        
        if skill.total_assessments > 0:
            return False, f"Cannot delete skill '{skill.name.value}' because it has been used in {skill.total_assessments} assessments"
        
        return True, "Skill can be deleted"
    
    async def recommend_skills_by_category(self, category: SkillCategory, limit: int = 5) -> List[Skill]:
        """
        Recomienda skills populares de una categoría específica
        """
        skills = await self._skill_repository.find_by_category(category)
        
        # Filtrar solo skills activas
        active_skills = [skill for skill in skills if skill.can_be_used_for_assessment()]
        
        # Ordenar por popularidad
        active_skills.sort(key=lambda s: s.get_popularity_score(), reverse=True)
        
        return active_skills[:limit]
    
    async def get_skill_progression_path(self, skill: Skill) -> List[Skill]:
        """
        Sugiere una ruta de progresión basada en dificultad
        Encuentra skills de la misma categoría con mayor dificultad
        """
        category_skills = await self._skill_repository.find_by_category(skill.category)
        
        # Filtrar skills activas con mayor dificultad
        progression_skills = [
            s for s in category_skills 
            if (s.can_be_used_for_assessment() and 
                s.difficulty_level.is_higher_than(skill.difficulty_level) and
                s.id != skill.id)
        ]
        
        # Ordenar por dificultad ascendente
        progression_skills.sort(key=lambda s: s.difficulty_level.get_numeric_level())
        
        return progression_skills
    
    async def calculate_category_coverage(self) -> dict:
        """
        Calcula la cobertura de skills por categoría
        Útil para identificar gaps en el catálogo de skills
        """
        all_skills = await self._skill_repository.find_active_skills()
        
        coverage = {}
        for skill in all_skills:
            category = skill.category.value
            difficulty = skill.difficulty_level.value
            
            if category not in coverage:
                coverage[category] = {
                    'total': 0,
                    'by_difficulty': {},
                    'average_score': 0.0,
                    'total_assessments': 0
                }
            
            coverage[category]['total'] += 1
            
            if difficulty not in coverage[category]['by_difficulty']:
                coverage[category]['by_difficulty'][difficulty] = 0
            coverage[category]['by_difficulty'][difficulty] += 1
            
            # Acumular métricas
            coverage[category]['total_assessments'] += skill.total_assessments
            coverage[category]['average_score'] += skill.average_score
        
        # Calcular promedios
        for category_data in coverage.values():
            if category_data['total'] > 0:
                category_data['average_score'] /= category_data['total']
        
        return coverage
    
    async def suggest_skill_improvements(self, skill: Skill) -> List[str]:
        """
        Sugiere mejoras para una skill basándose en métricas de uso
        """
        suggestions = []
        
        # Skill poco usada
        if skill.total_assessments < 5:
            suggestions.append("Consider improving skill visibility or relevance - low usage detected")
        
        # Score promedio bajo
        if skill.average_score < 60:
            suggestions.append("Review question difficulty - average score is low")
        
        # Sin tags
        if not skill.tags.value:
            suggestions.append("Add tags to improve discoverability")
        
        # Descripción muy corta
        if len(skill.description.value) < 50:
            suggestions.append("Expand skill description for better clarity")
        
        return suggestions
    
    async def bulk_status_change(self, skill_ids: List[str], new_status: str) -> dict:
        """
        Cambia el estado de múltiples skills de manera consistente
        Retorna un reporte de la operación
        """
        results = {
            'successful': [],
            'failed': [],
            'errors': []
        }
        
        for skill_id in skill_ids:
            try:
                skill = await self._skill_repository.find_by_id(skill_id)
                if not skill:
                    results['failed'].append(skill_id)
                    results['errors'].append(f"Skill {skill_id} not found")
                    continue
                
                from skill_management.domain.value_objects import SkillStatus
                status_vo = SkillStatus(new_status)
                skill.change_status(status_vo)
                
                await self._skill_repository.save_with_events(skill)
                results['successful'].append(skill_id)
                
            except Exception as e:
                results['failed'].append(skill_id)
                results['errors'].append(f"Error updating skill {skill_id}: {str(e)}")
        
        return results
