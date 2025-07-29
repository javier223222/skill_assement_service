"""
Excepciones específicas del dominio
Implementa jerarquía de excepciones para DDD
"""

from typing import Any, Dict, Optional


class DomainException(Exception):
    """Excepción base para todos los errores de dominio"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a diccionario para serialización"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationException(DomainException):
    """Excepción para errores de validación de dominio"""
    
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Validation failed for field '{field}' with value '{value}': {reason}"
        details = {
            "field": field,
            "value": str(value),
            "reason": reason
        }
        super().__init__(message, "VALIDATION_ERROR", details)


class BusinessRuleException(DomainException):
    """Excepción para violaciones de reglas de negocio"""
    
    def __init__(self, rule: str, context: Optional[Dict[str, Any]] = None):
        message = f"Business rule violation: {rule}"
        super().__init__(message, "BUSINESS_RULE_VIOLATION", context)


class EntityNotFoundException(DomainException):
    """Excepción cuando no se encuentra una entidad"""
    
    def __init__(self, entity_type: str, entity_id: str):
        message = f"{entity_type} with id '{entity_id}' not found"
        details = {
            "entity_type": entity_type,
            "entity_id": entity_id
        }
        super().__init__(message, "ENTITY_NOT_FOUND", details)


class AggregateNotFoundException(DomainException):
    """Excepción cuando no se encuentra un aggregate"""
    
    def __init__(self, aggregate_type: str, aggregate_id: str):
        message = f"{aggregate_type} aggregate with id '{aggregate_id}' not found"
        details = {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id
        }
        super().__init__(message, "AGGREGATE_NOT_FOUND", details)


class ConcurrencyException(DomainException):
    """Excepción para conflictos de concurrencia"""
    
    def __init__(self, entity_type: str, entity_id: str, expected_version: int, actual_version: int):
        message = f"Concurrency conflict for {entity_type} '{entity_id}': expected version {expected_version}, but was {actual_version}"
        details = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "expected_version": expected_version,
            "actual_version": actual_version
        }
        super().__init__(message, "CONCURRENCY_CONFLICT", details)


class InvariantViolationException(DomainException):
    """Excepción para violaciones de invariantes del dominio"""
    
    def __init__(self, invariant: str, aggregate_type: str, aggregate_id: str):
        message = f"Invariant violation in {aggregate_type} '{aggregate_id}': {invariant}"
        details = {
            "invariant": invariant,
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id
        }
        super().__init__(message, "INVARIANT_VIOLATION", details)


class DuplicateEntityException(DomainException):
    """Excepción para entidades duplicadas"""
    
    def __init__(self, entity_type: str, identifying_field: str, value: str):
        message = f"Duplicate {entity_type}: {identifying_field} '{value}' already exists"
        details = {
            "entity_type": entity_type,
            "identifying_field": identifying_field,
            "value": value
        }
        super().__init__(message, "DUPLICATE_ENTITY", details)


class InvalidOperationException(DomainException):
    """Excepción para operaciones inválidas en el estado actual"""
    
    def __init__(self, operation: str, current_state: str, entity_type: str):
        message = f"Cannot perform operation '{operation}' on {entity_type} in state '{current_state}'"
        details = {
            "operation": operation,
            "current_state": current_state,
            "entity_type": entity_type
        }
        super().__init__(message, "INVALID_OPERATION", details)


# Skill Management Domain Exceptions
class SkillDomainException(DomainException):
    """Excepción base para el dominio de Skills"""
    pass


class SkillAlreadyExistsException(SkillDomainException):
    """Excepción cuando ya existe una skill con el mismo nombre"""
    
    def __init__(self, skill_name: str):
        message = f"Skill '{skill_name}' already exists"
        super().__init__(message, "SKILL_ALREADY_EXISTS", {"skill_name": skill_name})


class InvalidSkillNameException(SkillDomainException):
    """Excepción para nombres de skill inválidos"""
    
    def __init__(self, skill_name: str, reason: str):
        message = f"Invalid skill name '{skill_name}': {reason}"
        super().__init__(message, "INVALID_SKILL_NAME", {"skill_name": skill_name, "reason": reason})


# Assessment Domain Exceptions
class AssessmentDomainException(DomainException):
    """Excepción base para el dominio de Assessment"""
    pass


class AssessmentAlreadyCompletedException(AssessmentDomainException):
    """Excepción cuando se intenta modificar una evaluación ya completada"""
    
    def __init__(self, assessment_id: str):
        message = f"Assessment '{assessment_id}' is already completed"
        super().__init__(message, "ASSESSMENT_ALREADY_COMPLETED", {"assessment_id": assessment_id})


class InvalidQuestionNumberException(AssessmentDomainException):
    """Excepción para números de pregunta inválidos"""
    
    def __init__(self, question_number: int, max_questions: int):
        message = f"Invalid question number {question_number}. Must be between 1 and {max_questions}"
        super().__init__(message, "INVALID_QUESTION_NUMBER", {
            "question_number": question_number,
            "max_questions": max_questions
        })


class QuestionAlreadyAnsweredException(AssessmentDomainException):
    """Excepción cuando se intenta responder una pregunta ya respondida"""
    
    def __init__(self, question_number: int, session_id: str):
        message = f"Question {question_number} in session '{session_id}' has already been answered"
        super().__init__(message, "QUESTION_ALREADY_ANSWERED", {
            "question_number": question_number,
            "session_id": session_id
        })


# Feedback Domain Exceptions
class FeedbackDomainException(DomainException):
    """Excepción base para el dominio de Feedback"""
    pass


class FeedbackAlreadyGeneratedException(FeedbackDomainException):
    """Excepción cuando ya existe feedback para una sesión"""
    
    def __init__(self, session_id: str):
        message = f"Feedback for session '{session_id}' has already been generated"
        super().__init__(message, "FEEDBACK_ALREADY_GENERATED", {"session_id": session_id})
