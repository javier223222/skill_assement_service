from domain.repositories.question_repository import QuestionRepository
from domain.repositories.user_session_repository import UserSessionRepository
from domain.repositories.assement_feedback_repository import AssementFeedBackRepository
from domain.repositories.skill_repository import SkillRepository
import asyncio
from typing import List
from typing import Dict, Any

from datetime import datetime

class GetFeedbacksByUser:
    def __init__(self, user_session_repository: UserSessionRepository, feedback_repository: AssementFeedBackRepository, skill_repository: SkillRepository,):
        self.user_session_repository = user_session_repository
        self.feedback_repository = feedback_repository
        self.skill_repository = skill_repository

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


    async def execute(self, user_id: str,skip:int=0,limit:int=10) -> Dict[str, Any]:
          try:
            user_sessions = await self.user_session_repository.get_session_finished_by_user_id(user_id, skip,limit)
            total_count = await self.user_session_repository.get_session_finished_by_user_id_count(user_id)
            total_pages = (total_count // limit) + (1 if total_count % limit > 0 else 0)
            feedbacks= []
            for session in user_sessions:
                feedback = await self.feedback_repository.get_feedback_minimal_by_session_id(str(session.id))
                if feedback:
                    skill = await self.skill_repository.find_by_id(session.skill_id)


                    feedbacks.append({
                        "session_id": str(session.id),
                        "user_id": session.user_id,
                        "finished_at": self.beautiful_date(session.finished_at),
                    
                        "skill_name": skill.name if skill else "Unknown Skill",
                        "feedback_id": feedback.get("id")


                       
                    })

            if not feedbacks:
                return {
                    "message": "No feedbacks found for this user",
                    "feedbacks": [],
                    "total_count": 0,
                    "total_pages": 0,
                    "current_page": 1,
                    "limit": limit
                }

            if not user_sessions:
                return {
                    "message": "No feedbacks found for this user",
                    "feedbacks": [],
                    "total_count": 0,
                    "total_pages": 0,
                    "current_page": 1,
                    "limit": limit
                }
            
           
           
            
            return {
                "message": "Feedbacks retrieved successfully",
                "feedbacks": feedbacks,
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": (skip // limit) + 1,
                "limit": limit

            }
          except Exception as e:
             
             raise Exception(f"Error fetching user sessions: {str(e)}")
        



           
