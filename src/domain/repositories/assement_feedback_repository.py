
from typing import Dict, Optional,List
from domain.entities.assement_feedback import AssementFeedback

from domain.repositories.base_repository import BaseRepository
from datetime import datetime
class AssementFeedBackRepository(BaseRepository[AssementFeedback]):
    def __init__(self):
        super().__init__(AssementFeedback)
    async def create_feedback(self, feedback: AssementFeedback) -> AssementFeedback:
      
        return await self.create(feedback)

    
    
    async def get_feedback_by_id(self, feedback_id: str) -> Optional[AssementFeedback]:
        """Obtener feedback por ID"""
        try:
            return await self.find_by_id(feedback_id)
        except Exception as e:
           
            return None

    async def get_feedback_by_session_id(self, session_id: str) -> Optional[AssementFeedback]:
        
        return await AssementFeedback.find_one(AssementFeedback.session_id == session_id)

    async def update_feedback(self, feedback_id: str, feedback: AssementFeedback) -> Optional[AssementFeedback]:
        feedback.updated_at = datetime.now()
        return await self.update_one({"_id": feedback_id}, feedback)
    async def get_all_feedbacks(self, limit: int = 10, skip: int = 0) -> List[AssementFeedback]:
        return await self.find_all(limit=limit, skip=skip)
    async def delete_feedback(self, feedback_id: str) -> bool:
        result = await self.delete_one({"_id": feedback_id})
        return result.deleted_count > 0



    async def get_feedback_minimal_by_session_id(self, session_id: str) -> Optional[Dict[str, str]]:
    
        pipeline = [
            {"$match": {"session_id": session_id}},
            {"$project": {
                "_id": 1,
                "user_id": 1, 
                "session_id": 1
            }},
            {"$limit": 1}
        ]
        
        result = await AssementFeedback.aggregate(pipeline).to_list()
        
        if result:
            doc = result[0]
            return {
                "id": str(doc["_id"]),
                "user_id": doc["user_id"],
                "session_id": doc["session_id"]
            }
        return None