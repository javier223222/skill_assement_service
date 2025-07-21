from dataclasses import dataclass
from enum import Enum

class QuestionTypeEnum(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"

@dataclass(frozen=True)
class QuestionType:
    value: str
    display_name: str
    description: str
    
    def __post_init__(self):
        if self.value not in [e.value for e in QuestionTypeEnum]:
            raise ValueError(f"Invalid question type: {self.value}")
    
    @classmethod
    def multiple_choice(cls) -> 'QuestionType':
        return cls(
            value="multiple_choice",
            display_name="Multiple Choice",
            description="Question with multiple options where only one is correct"
        )
    
    @classmethod
    def true_false(cls) -> 'QuestionType':
        return cls(
            value="true_false",
            display_name="True/False",
            description="Question with only true or false options"
        )
    
    @classmethod
    def open_ended(cls) -> 'QuestionType':
        return cls(
            value="open_ended",
            display_name="Open Ended",
            description="Question requiring a free-form text response"
        )
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, QuestionType):
            return self.value == other.value
        return self.value == other