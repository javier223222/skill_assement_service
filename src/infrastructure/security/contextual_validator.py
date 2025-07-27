"""
Middleware y utilidades para validación contextual avanzada.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, ValidationError


class ValidationContext:
    """Contexto para validaciones avanzadas."""
    
    def __init__(self):
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.skill_id: Optional[str] = None
        self.request_timestamp: datetime = datetime.now(timezone.utc)
        self.additional_data: Dict[str, Any] = {}
    
    def set_user_context(self, user_id: str):
        """Establece el contexto del usuario."""
        self.user_id = user_id
    
    def set_session_context(self, session_id: str):
        """Establece el contexto de la sesión."""
        self.session_id = session_id
    
    def set_skill_context(self, skill_id: str):
        """Establece el contexto de la habilidad."""
        self.skill_id = skill_id


class ContextualValidator:
    """Validador que considera el contexto de la aplicación."""
    
    @staticmethod
    def validate_session_ownership(user_id: str, session_user_id: str) -> bool:
        """
        Valida que la sesión pertenezca al usuario correcto.
        
        Args:
            user_id: ID del usuario autenticado
            session_user_id: ID del usuario de la sesión
            
        Returns:
            True si la sesión pertenece al usuario
            
        Raises:
            ValidationError: Si la validación falla
        """
        if user_id != session_user_id:
            raise ValidationError("Session does not belong to authenticated user")
        return True
    
    @staticmethod
    def validate_question_sequence(current_question: int, expected_question: int) -> bool:
        """
        Valida que las preguntas se respondan en secuencia.
        
        Args:
            current_question: Pregunta actual en la sesión
            expected_question: Pregunta que se está intentando responder
            
        Returns:
            True si la secuencia es correcta
            
        Raises:
            ValidationError: Si la secuencia es incorrecta
        """
        if expected_question != current_question:
            raise ValidationError(f"Expected question {current_question}, got {expected_question}")
        return True
    
    @staticmethod
    def validate_session_expiry(session_created: datetime, max_duration_hours: int = 2) -> bool:
        """
        Valida que la sesión no haya expirado.
        
        Args:
            session_created: Timestamp de creación de la sesión
            max_duration_hours: Duración máxima en horas
            
        Returns:
            True si la sesión es válida
            
        Raises:
            ValidationError: Si la sesión ha expirado
        """
        now = datetime.now(timezone.utc)
        duration = now - session_created
        max_duration = max_duration_hours * 3600  # Convertir a segundos
        
        if duration.total_seconds() > max_duration:
            raise ValidationError("Session has expired")
        return True
    
    @staticmethod
    def validate_skill_question_relationship(skill_id: str, question_skill_id: str) -> bool:
        """
        Valida que la pregunta pertenezca a la habilidad correcta.
        
        Args:
            skill_id: ID de la habilidad de la sesión
            question_skill_id: ID de la habilidad de la pregunta
            
        Returns:
            True si la relación es correcta
            
        Raises:
            ValidationError: Si la pregunta no pertenece a la habilidad
        """
        if skill_id != question_skill_id:
            raise ValidationError("Question does not belong to the specified skill")
        return True
    
    @staticmethod
    def validate_daily_assessment_limit(user_assessments_today: int, max_daily: int = 5) -> bool:
        """
        Valida límite diario de evaluaciones por usuario.
        
        Args:
            user_assessments_today: Número de evaluaciones del usuario hoy
            max_daily: Máximo número de evaluaciones diarias
            
        Returns:
            True si no se ha excedido el límite
            
        Raises:
            ValidationError: Si se ha excedido el límite
        """
        if user_assessments_today >= max_daily:
            raise ValidationError(f"Daily assessment limit of {max_daily} exceeded")
        return True


class BusinessRuleValidator:
    """Validador de reglas de negocio específicas."""
    
    @staticmethod
    def validate_assessment_completeness(answered_questions: int, total_questions: int) -> bool:
        """
        Valida que se hayan respondido todas las preguntas antes de generar feedback.
        
        Args:
            answered_questions: Número de preguntas respondidas
            total_questions: Total de preguntas en la evaluación
            
        Returns:
            True si la evaluación está completa
            
        Raises:
            ValidationError: Si la evaluación no está completa
        """
        if answered_questions < total_questions:
            raise ValidationError(
                f"Assessment incomplete: {answered_questions}/{total_questions} questions answered"
            )
        return True
    
    @staticmethod
    def validate_skill_prerequisites(skill_id: str, user_completed_skills: list) -> bool:
        """
        Valida que el usuario tenga las habilidades prerequisito.
        
        Args:
            skill_id: ID de la habilidad a evaluar
            user_completed_skills: Lista de habilidades completadas por el usuario
            
        Returns:
            True si se cumplen los prerequisitos
        """
        # Aquí se pueden definir reglas específicas de prerequisitos
        # Por ahora, permitir todas las habilidades
        return True
    
    @staticmethod
    def validate_answer_format(answer: str, question_type: str) -> bool:
        """
        Valida que la respuesta tenga el formato correcto según el tipo de pregunta.
        
        Args:
            answer: Respuesta del usuario
            question_type: Tipo de pregunta
            
        Returns:
            True si el formato es correcto
            
        Raises:
            ValidationError: Si el formato es incorrecto
        """
        if question_type == "multiple_choice":
            # Para multiple choice, validar que la respuesta no esté vacía
            if not answer.strip():
                raise ValidationError("Answer cannot be empty for multiple choice questions")
        
        elif question_type == "true_false":
            # Para verdadero/falso, validar respuestas específicas
            valid_answers = ["true", "false", "verdadero", "falso", "sí", "no", "yes", "no"]
            if answer.lower().strip() not in valid_answers:
                raise ValidationError("Invalid answer for true/false question")
        
        return True
