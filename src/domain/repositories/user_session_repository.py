from typing import List, Optional
from domain.entities.user_session import UserSession

from domain.repositories.base_repository import BaseRepository


class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self):
        super().__init__(UserSession)

    async def create_user_session(self, user_session: UserSession) -> UserSession:
        return await self.create(user_session)

    async def get_user_session_by_id(self, session_id: str) -> Optional[UserSession]:
        return await self.find_by_id(session_id)
    async def get_session_finished_by_user_id(self, user_id: str,  skip: int, limit: int) -> List[UserSession]:
        return await UserSession.find(
            UserSession.user_id == user_id, 
            UserSession.is_finished == True
        ).skip(skip).limit(limit).to_list()
    async def get_session_finished_by_user_id_count(self, user_id: str) -> int:
        count = await UserSession.find(
            UserSession.user_id == user_id, 
            UserSession.is_finished == True
        ).count()
        return count if count is not None else 0
    

    async def update_user_session(self, user_session: UserSession) -> UserSession:
        return await self.update(user_session)

    async def delete_user_session(self, session_id: str) -> bool:
        return await self.delete_by_id(session_id)
    

    async def find_all_sessions(self, limit: int = 10, skip: int = 0) -> List[UserSession]:
        return await self.find_all(limit, skip)