"""
Value Objects para el dominio de Skill Management
"""

from typing import List, Optional
from shared.domain.base_value_object import StringValueObject, EnumValueObject
import re


class SkillName(StringValueObject):
    """Value Object para nombres de skills"""
    
    def __init__(self, value: str):
        # Validaciones específicas para nombres de skills
        cleaned_value = value.strip()
        
        if len(cleaned_value) < 2:
            raise ValueError("Skill name must be at least 2 characters long")
        
        if len(cleaned_value) > 100:
            raise ValueError("Skill name cannot exceed 100 characters")
        
        # Solo letras, números, espacios, guiones y puntos
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', cleaned_value):
            raise ValueError("Skill name can only contain letters, numbers, spaces, hyphens, and dots")
        
        super().__init__(value=cleaned_value)
    
    def to_slug(self) -> str:
        """Convierte el nombre a un slug URL-friendly"""
        return re.sub(r'[^a-zA-Z0-9]+', '-', self.value.lower()).strip('-')


class SkillDescription(StringValueObject):
    """Value Object para descripciones de skills"""
    
    def __init__(self, value: str):
        cleaned_value = value.strip()
        
        if len(cleaned_value) < 10:
            raise ValueError("Skill description must be at least 10 characters long")
        
        if len(cleaned_value) > 1000:
            raise ValueError("Skill description cannot exceed 1000 characters")
        
        super().__init__(value=cleaned_value)
    
    def get_summary(self, max_length: int = 100) -> str:
        """Obtiene un resumen de la descripción"""
        if len(self.value) <= max_length:
            return self.value
        
        # Corta en la palabra más cercana
        summary = self.value[:max_length]
        last_space = summary.rfind(' ')
        if last_space > max_length * 0.8:  # Si hay un espacio cercano al final
            summary = summary[:last_space]
        
        return summary + "..."


class DifficultyLevel(EnumValueObject):
    """Value Object para niveles de dificultad"""
    
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    
    def __init__(self, value: str):
        allowed_values = [self.BEGINNER, self.INTERMEDIATE, self.ADVANCED, self.EXPERT]
        super().__init__(value=value.lower(), allowed_values=allowed_values)
    
    def get_numeric_level(self) -> int:
        """Convierte el nivel a un valor numérico para comparaciones"""
        levels = {
            self.BEGINNER: 1,
            self.INTERMEDIATE: 2,
            self.ADVANCED: 3,
            self.EXPERT: 4
        }
        return levels[self.value]
    
    def is_higher_than(self, other: 'DifficultyLevel') -> bool:
        """Verifica si este nivel es mayor que otro"""
        return self.get_numeric_level() > other.get_numeric_level()


class SkillCategory(EnumValueObject):
    """Value Object para categorías de skills"""
    
    PROGRAMMING = "programming"
    DATABASE = "database"
    DEVOPS = "devops"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MOBILE = "mobile"
    TESTING = "testing"
    SECURITY = "security"
    AI_ML = "ai_ml"
    DATA_SCIENCE = "data_science"
    CLOUD = "cloud"
    OTHER = "other"
    
    def __init__(self, value: str):
        allowed_values = [
            self.PROGRAMMING, self.DATABASE, self.DEVOPS, self.FRONTEND,
            self.BACKEND, self.MOBILE, self.TESTING, self.SECURITY,
            self.AI_ML, self.DATA_SCIENCE, self.CLOUD, self.OTHER
        ]
        super().__init__(value=value.lower(), allowed_values=allowed_values)
    
    def get_display_name(self) -> str:
        """Obtiene el nombre para mostrar en UI"""
        display_names = {
            self.PROGRAMMING: "Programming",
            self.DATABASE: "Database",
            self.DEVOPS: "DevOps",
            self.FRONTEND: "Frontend",
            self.BACKEND: "Backend",
            self.MOBILE: "Mobile Development",
            self.TESTING: "Testing",
            self.SECURITY: "Security",
            self.AI_ML: "AI/Machine Learning",
            self.DATA_SCIENCE: "Data Science",
            self.CLOUD: "Cloud Computing",
            self.OTHER: "Other"
        }
        return display_names[self.value]


class SkillTags(StringValueObject):
    """Value Object para tags de skills"""
    
    def __init__(self, value: str):
        cleaned_value = value.strip()
        
        if len(cleaned_value) > 500:
            raise ValueError("Skill tags cannot exceed 500 characters")
        
        # Validar formato de tags (separados por comas)
        if cleaned_value and not re.match(r'^[a-zA-Z0-9\s,\-\.]+$', cleaned_value):
            raise ValueError("Tags can only contain letters, numbers, spaces, commas, hyphens, and dots")
        
        super().__init__(value=cleaned_value)
    
    def get_tags_list(self) -> List[str]:
        """Convierte el string de tags en una lista"""
        if not self.value:
            return []
        
        return [tag.strip() for tag in self.value.split(',') if tag.strip()]
    
    def add_tag(self, tag: str) -> 'SkillTags':
        """Agrega un nuevo tag (retorna nuevo objeto inmutable)"""
        current_tags = self.get_tags_list()
        tag = tag.strip().lower()
        
        if tag and tag not in [t.lower() for t in current_tags]:
            current_tags.append(tag)
        
        return SkillTags(', '.join(current_tags))
    
    def remove_tag(self, tag: str) -> 'SkillTags':
        """Remueve un tag (retorna nuevo objeto inmutable)"""
        current_tags = self.get_tags_list()
        tag = tag.strip().lower()
        
        filtered_tags = [t for t in current_tags if t.lower() != tag]
        return SkillTags(', '.join(filtered_tags))


class SkillStatus(EnumValueObject):
    """Value Object para estado de skills"""
    
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    
    def __init__(self, value: str):
        allowed_values = [self.DRAFT, self.ACTIVE, self.INACTIVE, self.ARCHIVED]
        super().__init__(value=value.lower(), allowed_values=allowed_values)
    
    def can_transition_to(self, new_status: 'SkillStatus') -> bool:
        """Verifica si se puede transicionar a un nuevo estado"""
        valid_transitions = {
            self.DRAFT: [self.ACTIVE, self.ARCHIVED],
            self.ACTIVE: [self.INACTIVE, self.ARCHIVED],
            self.INACTIVE: [self.ACTIVE, self.ARCHIVED],
            self.ARCHIVED: []  # No se puede salir del estado archivado
        }
        
        return new_status.value in valid_transitions.get(self.value, [])
    
    def is_available_for_assessment(self) -> bool:
        """Verifica si la skill está disponible para evaluaciones"""
        return self.value == self.ACTIVE
