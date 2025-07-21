
from domain.repositories.question_repository import QuestionRepository
from domain.repositories.user_session_repository import UserSessionRepository

class BaseAssessmentUseCase:
    """
    Base class for assessment use cases.
    This class can be extended by specific use cases to implement their logic.
    """

    def __init__(self, question_repository: QuestionRepository, user_session_repository: UserSessionRepository):
        self.question_repository = question_repository
        self.user_session_repository = user_session_repository

    async def execute(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")