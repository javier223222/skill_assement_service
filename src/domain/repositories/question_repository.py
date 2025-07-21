from typing import Dict, Optional,List
from domain.entities.question import Question
from domain.repositories.base_repository import BaseRepository
from datetime import datetime
class QuestionRepository(BaseRepository[Question]):
    def __init__(self):
        super().__init__(Question)
    
    async def create_question(self, question_data: Dict) -> Question:
        question = Question(
            id=question_data.get("id"),
            skillid=question_data.get("skillid"),
            subcategory=question_data.get("subcategory"),
            type=question_data.get("type"),
            question=question_data.get("question"),
            options=question_data.get("options", []),
            correct_answer=question_data.get("correct_answer"),
            created_at=datetime.now(),
            updated_at=None
        )
        await question.insert()
        return question

    async def get_question_by_skillid(self,skillId: str) -> Optional[List[Question]]:
        return await self.model_class.find(Question.skillid ==skillId )
    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        return await self.model_class.find_one(Question.id == question_id)
    async def find_question_by_skillid_and_number(self, skill_id: str, number: int) -> Optional[Question]:
        return await self.model_class.find_one(Question.skillid == skill_id, Question.id == number)
    async def find_questions_by_skillid(self, skill_id: str) -> Optional[List[Question]]:
        return await self.model_class.find(Question.skillid == skill_id).to_list()
    async def count_questions_by_skillid(self, skill_id: str) -> int:
        count = await self.model_class.find(Question.skillid == skill_id).count()
        return count if count is not None else 0
    
    async def delete_many_by_skillid(self, skill_id: str) -> int:
        result = await self.model_class.find(Question.skillid == skill_id).delete()
        return result.deleted_count if result else 0
    

    
    