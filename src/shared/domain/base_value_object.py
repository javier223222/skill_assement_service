"""
Base Value Object para implementar Value Objects siguiendo DDD
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union
from pydantic import BaseModel, validator


class BaseValueObject(BaseModel, ABC):
    """
    Clase base para todos los Value Objects
    
    Características:
    - Inmutabilidad
    - Igualdad por valor
    - Autovalidación
    - Sin identidad
    """
    
    class Config:
        # Hace los objetos inmutables
        allow_mutation = False
        # Valida al asignar
        validate_assignment = True
        # Usa enum values
        use_enum_values = True
    
    @abstractmethod
    def __str__(self) -> str:
        """Representación string del value object"""
        pass
    
    def __eq__(self, other: object) -> bool:
        """Igualdad basada en valores, no en identidad"""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        """Hash basado en los valores"""
        return hash(tuple(sorted(self.__dict__.items())))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el value object a diccionario"""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseValueObject':
        """Crea un value object desde un diccionario"""
        return cls(**data)


class StringValueObject(BaseValueObject):
    """Value Object para strings con validaciones comunes"""
    
    value: str
    
    @validator('value')
    def value_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Value cannot be empty or whitespace')
        return v.strip()
    
    def __str__(self) -> str:
        return self.value
    
    def __len__(self) -> int:
        return len(self.value)


class NumericValueObject(BaseValueObject):
    """Value Object para números con validaciones comunes"""
    
    value: Union[int, float]
    
    @validator('value')
    def value_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Value must be positive')
        return v
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return int(self.value)
    
    def __float__(self) -> float:
        return float(self.value)


class EnumValueObject(BaseValueObject):
    """Value Object para enumeraciones"""
    
    value: str
    allowed_values: List[str] = []
    
    @validator('value')
    def value_must_be_allowed(cls, v, values):
        allowed = values.get('allowed_values', [])
        if allowed and v not in allowed:
            raise ValueError(f'Value must be one of: {allowed}')
        return v
    
    def __str__(self) -> str:
        return self.value


class PercentageValueObject(NumericValueObject):
    """Value Object específico para porcentajes"""
    
    @validator('value')
    def value_must_be_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v


class EmailValueObject(StringValueObject):
    """Value Object para emails"""
    
    @validator('value')
    def value_must_be_valid_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()


class IdValueObject(StringValueObject):
    """Value Object para identificadores"""
    
    @validator('value')
    def value_must_be_valid_id(cls, v):
        from bson import ObjectId
        try:
            ObjectId(v)
        except:
            raise ValueError('Invalid ObjectId format')
        return v
