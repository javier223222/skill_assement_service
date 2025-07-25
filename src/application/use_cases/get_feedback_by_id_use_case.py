
from domain.repositories.assement_feedback_repository import AssementFeedBackRepository
from domain.repositories.skill_repository import SkillRepository
from domain.repositories.user_session_repository import UserSessionRepository
import asyncio
from typing import List
from typing import Dict, Any

from datetime import datetime

class GetFeedBackByIdUseCase:
    def __init__(self, feedback_repository: AssementFeedBackRepository, skill_repository: SkillRepository, user_session_repository: UserSessionRepository):
        self.feedback_repository = feedback_repository
        self.skill_repository = skill_repository
        self.user_session_repository = user_session_repository
    def beautiful_date(self, date_obj: datetime) -> str:
        """Get friendly date in English"""
        if not date_obj:
            return "Unknown Date"
            
        months_en = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        
        days_en = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
            4: "Friday", 5: "Saturday", 6: "Sunday"
        }
        
        day_name = days_en.get(date_obj.weekday(), "")
        month_name = months_en.get(date_obj.month, "")
        
        return f"{day_name}, {month_name} {date_obj.day}, {date_obj.year}"
    async def execute(self, feedback_id: str) -> Dict[str, Any]:
        try:
            feedback = await self.feedback_repository.get_feedback_by_id(feedback_id)
            print(f"Feedback retrieved: {feedback}")
            session= await self.user_session_repository.get_user_session_by_id(feedback.session_id)
            skill = await self.skill_repository.find_by_id(session.skill_id) if session else None

            return {
                "feedback": feedback,
                "skill_name": skill.name if skill else "Unknown Skill",
            }
           
        except Exception as e:
            raise Exception(f"Error retrieving feedback by ID: {str(e)}")
