"""
Módulo de sanitización de entrada para prevenir ataques XSS e injection.
Implementa las mejores prácticas de seguridad para validación de datos.
"""

import html
import re
from typing import Any, Optional
from pydantic import validator


class InputSanitizer:
    """Clase para sanitizar y validar datos de entrada."""
    
    # Patrones regex para validación
    SAFE_TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.()áéíóúÁÉÍÓÚñÑ]+$')
    DANGEROUS_PATTERNS = [
        re.compile(r'<script[\s\S]*?</script>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'(union|select|insert|delete|drop|update|alter|create|exec)', re.IGNORECASE),
    ]
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000, allow_special_chars: bool = False) -> str:
        """
        Sanitiza texto eliminando caracteres peligrosos.
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima permitida
            allow_special_chars: Si permite caracteres especiales seguros
            
        Returns:
            Texto sanitizado
            
        Raises:
            ValueError: Si el input no es válido
        """
        if not isinstance(text, str):
            raise ValueError("Input must be string")
        
        if not text.strip():
            raise ValueError("Input cannot be empty")
        
        # Limitar longitud
        if len(text) > max_length:
            raise ValueError(f"Text length cannot exceed {max_length} characters")
        
        # Detectar patrones peligrosos
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if pattern.search(text):
                raise ValueError("Potentially dangerous content detected")
        
        # Eliminar caracteres peligrosos básicos
        if not allow_special_chars:
            text = re.sub(r'[<>\"\'&]', '', text)
        
        # Trim espacios
        text = text.strip()
        
        # Validar patrón seguro si no se permiten caracteres especiales
        if not allow_special_chars and not InputSanitizer.SAFE_TEXT_PATTERN.match(text):
            raise ValueError("Text contains invalid characters")
        
        return text
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Escapa caracteres HTML para prevenir XSS.
        
        Args:
            text: Texto a escapar
            
        Returns:
            Texto con caracteres HTML escapados
        """
        if not isinstance(text, str):
            raise ValueError("Input must be string")
        
        return html.escape(text)
    
    @staticmethod
    def sanitize_skill_name(name: str) -> str:
        """
        Sanitiza nombres de habilidades con reglas específicas.
        
        Args:
            name: Nombre de la habilidad
            
        Returns:
            Nombre sanitizado
        """
        return InputSanitizer.sanitize_text(
            name, 
            max_length=100, 
            allow_special_chars=True
        )
    
    @staticmethod
    def sanitize_description(description: str) -> str:
        """
        Sanitiza descripciones con reglas específicas.
        
        Args:
            description: Descripción a sanitizar
            
        Returns:
            Descripción sanitizada
        """
        return InputSanitizer.sanitize_text(
            description, 
            max_length=500, 
            allow_special_chars=True
        )
    
    @staticmethod
    def sanitize_answer(answer: str) -> str:
        """
        Sanitiza respuestas de usuarios.
        
        Args:
            answer: Respuesta del usuario
            
        Returns:
            Respuesta sanitizada
        """
        return InputSanitizer.sanitize_text(
            answer, 
            max_length=2000, 
            allow_special_chars=True
        )
    
    @staticmethod
    def validate_id_format(id_value: str) -> str:
        """
        Valida formato de IDs.
        
        Args:
            id_value: ID a validar
            
        Returns:
            ID validado
            
        Raises:
            ValueError: Si el ID no es válido
        """
        if not isinstance(id_value, str):
            raise ValueError("ID must be string")
        
        if not id_value.strip():
            raise ValueError("ID cannot be empty")
        
        # Validar que solo contenga caracteres seguros para IDs
        if not re.match(r'^[a-zA-Z0-9_-]+$', id_value):
            raise ValueError("ID contains invalid characters")
        
        if len(id_value) > 50:
            raise ValueError("ID too long")
        
        return id_value.strip()


def create_sanitizer_validator(field_type: str = "text", max_length: int = 1000):
    """
    Factory function para crear validadores de sanitización personalizados.
    
    Args:
        field_type: Tipo de campo (text, name, description, answer, id)
        max_length: Longitud máxima
        
    Returns:
        Función validadora
    """
    def validator_func(cls, v):
        if v is None:
            return v
        
        if field_type == "name":
            return InputSanitizer.sanitize_skill_name(v)
        elif field_type == "description":
            return InputSanitizer.sanitize_description(v)
        elif field_type == "answer":
            return InputSanitizer.sanitize_answer(v)
        elif field_type == "id":
            return InputSanitizer.validate_id_format(v)
        else:
            return InputSanitizer.sanitize_text(v, max_length)
    
    return validator_func
