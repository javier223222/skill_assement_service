"""
Value Objects para el dominio de Assessment
"""

from typing import List, Optional
from shared.domain.base_value_object import (
    StringValueObject, NumericValueObject, EnumValueObject, IdValueObject
)
import re


class SessionId(IdValueObject):
    """Value Object para identificadores de sesión"""
    pass


class QuestionNumber(NumericValueObject):
    """Value Object para números de pregunta"""
    
    def __init__(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Question number must be an integer")
        
        if value < 1:
            raise ValueError("Question number must be positive")
        
        if value > 50:  # Límite razonable
            raise ValueError("Question number cannot exceed 50")
        
        super().__init__(value=value)
    
    def is_first_question(self) -> bool:
        """Verifica si es la primera pregunta"""
        return self.value == 1
    
    def next_question(self) -> 'QuestionNumber':
        """Retorna el número de la siguiente pregunta"""
        return QuestionNumber(self.value + 1)
    
    def previous_question(self) -> Optional['QuestionNumber']:
        """Retorna el número de la pregunta anterior"""
        if self.value <= 1:
            return None
        return QuestionNumber(self.value - 1)


class QuestionText(StringValueObject):
    """Value Object para texto de preguntas"""
    
    def __init__(self, value: str):
        cleaned_value = value.strip()
        
        if len(cleaned_value) < 10:
            raise ValueError("Question text must be at least 10 characters long")
        
        if len(cleaned_value) > 1000:
            raise ValueError("Question text cannot exceed 1000 characters")
        
        # Verificar que termine con signo de interrogación
        if not cleaned_value.endswith('?'):
            cleaned_value += '?'
        
        super().__init__(value=cleaned_value)
    
    def get_word_count(self) -> int:
        """Obtiene el número de palabras en la pregunta"""
        return len(self.value.split())
    
    def is_complex_question(self) -> bool:
        """Determina si es una pregunta compleja basándose en la longitud"""
        return self.get_word_count() > 20


class AnswerOption(StringValueObject):
    """Value Object para opciones de respuesta"""
    
    def __init__(self, value: str):
        cleaned_value = value.strip()
        
        if len(cleaned_value) < 1:
            raise ValueError("Answer option cannot be empty")
        
        if len(cleaned_value) > 200:
            raise ValueError("Answer option cannot exceed 200 characters")
        
        super().__init__(value=cleaned_value)


class AnswerOptions(StringValueObject):
    """Value Object para conjunto de opciones de respuesta"""
    
    def __init__(self, options: List[str]):
        if not options:
            raise ValueError("At least one answer option is required")
        
        if len(options) < 2:
            raise ValueError("At least two answer options are required")
        
        if len(options) > 6:
            raise ValueError("Cannot have more than 6 answer options")
        
        # Validar y limpiar cada opción
        validated_options = []
        for option in options:
            answer_option = AnswerOption(option)
            validated_options.append(answer_option.value)
        
        # Verificar duplicados
        if len(set(validated_options)) != len(validated_options):
            raise ValueError("Answer options must be unique")
        
        # Convertir a string separado por |
        options_string = "|".join(validated_options)
        super().__init__(value=options_string)
    
    def get_options_list(self) -> List[str]:
        """Convierte el string de opciones en una lista"""
        return self.value.split("|")
    
    def get_option_by_index(self, index: int) -> Optional[str]:
        """Obtiene una opción por su índice"""
        options = self.get_options_list()
        if 0 <= index < len(options):
            return options[index]
        return None
    
    def contains_option(self, option: str) -> bool:
        """Verifica si contiene una opción específica"""
        return option in self.get_options_list()
    
    def get_options_count(self) -> int:
        """Obtiene el número de opciones"""
        return len(self.get_options_list())


class CorrectAnswer(StringValueObject):
    """Value Object para respuesta correcta"""
    
    def __init__(self, value: str, valid_options: AnswerOptions):
        cleaned_value = value.strip()
        
        if not cleaned_value:
            raise ValueError("Correct answer cannot be empty")
        
        # Verificar que la respuesta correcta esté en las opciones válidas
        if not valid_options.contains_option(cleaned_value):
            raise ValueError(f"Correct answer '{cleaned_value}' must be one of the valid options")
        
        super().__init__(value=cleaned_value)
    
    def get_option_index(self, options: AnswerOptions) -> int:
        """Obtiene el índice de la respuesta correcta en las opciones"""
        options_list = options.get_options_list()
        try:
            return options_list.index(self.value)
        except ValueError:
            return -1


class UserAnswer(StringValueObject):
    """Value Object para respuesta del usuario"""
    
    def __init__(self, value: str, valid_options: AnswerOptions):
        cleaned_value = value.strip()
        
        if not cleaned_value:
            raise ValueError("User answer cannot be empty")
        
        # Verificar que la respuesta esté en las opciones válidas
        if not valid_options.contains_option(cleaned_value):
            raise ValueError(f"User answer '{cleaned_value}' must be one of the valid options")
        
        super().__init__(value=cleaned_value)
    
    def is_correct(self, correct_answer: CorrectAnswer) -> bool:
        """Verifica si la respuesta del usuario es correcta"""
        return self.value == correct_answer.value


class Subcategory(StringValueObject):
    """Value Object para subcategorías de preguntas"""
    
    def __init__(self, value: str):
        cleaned_value = value.strip()
        
        if len(cleaned_value) < 2:
            raise ValueError("Subcategory must be at least 2 characters long")
        
        if len(cleaned_value) > 50:
            raise ValueError("Subcategory cannot exceed 50 characters")
        
        # Solo letras, números, espacios y guiones
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', cleaned_value):
            raise ValueError("Subcategory can only contain letters, numbers, spaces, and hyphens")
        
        super().__init__(value=cleaned_value)


class QuestionType(EnumValueObject):
    """Value Object para tipos de pregunta"""
    
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SINGLE_CHOICE = "single_choice"
    
    def __init__(self, value: str):
        allowed_values = [self.MULTIPLE_CHOICE, self.TRUE_FALSE, self.SINGLE_CHOICE]
        super().__init__(value=value.lower(), allowed_values=allowed_values)
    
    def get_display_name(self) -> str:
        """Obtiene el nombre para mostrar en UI"""
        display_names = {
            self.MULTIPLE_CHOICE: "Multiple Choice",
            self.TRUE_FALSE: "True/False",
            self.SINGLE_CHOICE: "Single Choice"
        }
        return display_names[self.value]
    
    def get_max_options(self) -> int:
        """Obtiene el número máximo de opciones para este tipo"""
        max_options = {
            self.MULTIPLE_CHOICE: 6,
            self.TRUE_FALSE: 2,
            self.SINGLE_CHOICE: 4
        }
        return max_options[self.value]


class AssessmentStatus(EnumValueObject):
    """Value Object para estados de evaluación"""
    
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"
    
    def __init__(self, value: str):
        allowed_values = [
            self.NOT_STARTED, self.IN_PROGRESS, self.COMPLETED, 
            self.ABANDONED, self.EXPIRED
        ]
        super().__init__(value=value.lower(), allowed_values=allowed_values)
    
    def can_transition_to(self, new_status: 'AssessmentStatus') -> bool:
        """Verifica si se puede transicionar a un nuevo estado"""
        valid_transitions = {
            self.NOT_STARTED: [self.IN_PROGRESS, self.ABANDONED],
            self.IN_PROGRESS: [self.COMPLETED, self.ABANDONED, self.EXPIRED],
            self.COMPLETED: [],  # Estado final
            self.ABANDONED: [],  # Estado final
            self.EXPIRED: []     # Estado final
        }
        
        return new_status.value in valid_transitions.get(self.value, [])
    
    def is_final_status(self) -> bool:
        """Verifica si es un estado final"""
        return self.value in [self.COMPLETED, self.ABANDONED, self.EXPIRED]
    
    def is_active(self) -> bool:
        """Verifica si la evaluación está activa"""
        return self.value == self.IN_PROGRESS


class Score(NumericValueObject):
    """Value Object para puntajes"""
    
    def __init__(self, value: float):
        if not 0 <= value <= 100:
            raise ValueError("Score must be between 0 and 100")
        
        # Redondear a 2 decimales
        rounded_value = round(value, 2)
        super().__init__(value=rounded_value)
    
    def get_letter_grade(self) -> str:
        """Convierte el puntaje a una calificación por letras"""
        if self.value >= 90:
            return "A"
        elif self.value >= 80:
            return "B"
        elif self.value >= 70:
            return "C"
        elif self.value >= 60:
            return "D"
        else:
            return "F"
    
    def is_passing_score(self, passing_threshold: float = 60.0) -> bool:
        """Verifica si es un puntaje aprobatorio"""
        return self.value >= passing_threshold
    
    def get_performance_level(self) -> str:
        """Obtiene el nivel de rendimiento"""
        if self.value >= 90:
            return "Excellent"
        elif self.value >= 80:
            return "Good"
        elif self.value >= 70:
            return "Average"
        elif self.value >= 60:
            return "Below Average"
        else:
            return "Poor"
