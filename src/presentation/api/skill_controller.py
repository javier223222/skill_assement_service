from fastapi import APIRouter,Depends, HTTPException,status
from typing import List
from domain.entities.skill import Skill
from application.use_cases.create_skill_use_case import CreateSkillUseCase
from application.use_cases.get_all_skills_use_case import GetAllSkillsUseCase
from application.use_cases.get_skill_use_case import GetSkillUseCase
from application.use_cases.delete_skill_use_case import DeleteSkillUseCase
from application.use_cases.update_skill_use_case import UpdateSkillUseCase
from ..schemas.create_skill_model import CreateSkillModel
from ..schemas.update_skill_model import UpdateSkillModel
from domain.repositories.skill_repository import SkillRepository
from ..schemas.get_all_skill_response_model import GetAllSkillResponseModel
from domain.repositories.question_repository import QuestionRepository
from pydantic import ValidationError

import json
skill_router = APIRouter(prefix="/skills",tags=["Skills"])

@skill_router.post("/",response_model=Skill,status_code=status.HTTP_201_CREATED)
async def create_skill(skill: CreateSkillModel):
    try:
        skill_repository = SkillRepository()
        create_skill_use_case = CreateSkillUseCase(skill_repository)
        
        created_skill = await create_skill_use_case.execute(skill=Skill(**skill.model_dump()))

        created_skill = await create_skill_use_case.execute(Skill(**skill.dict()))
        
        return json.loads(created_skill.model_dump_json())
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Error de validación: {str(e)}")
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=str(e))

@skill_router.get("/skills/", response_model=GetAllSkillResponseModel)
async def get_all_skills(skip: int = 0, limit: int = 10):
    try:
        skill_repository = SkillRepository()
        get_all_skills_use_case = GetAllSkillsUseCase(skill_repository)
        
        result = await get_all_skills_use_case.execute(skip=skip, limit=limit)
        
        return {
            "total_skills": result.total_skills,
            "total_pages": result.total_pages,
            "has_next_page": result.has_next_page,
            "has_previous_page": result.has_previous_page,
            "current_page": result.current_page,
            "limit": result.limit,
            "skills": result.skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@skill_router.get("/{skill_id}", response_model=Skill)
async def get_skill_by_id(skill_id: str):
    try:
        skill_repository = SkillRepository()
        get_skill_use_case = GetSkillUseCase(skill_repository)
        skill = await get_skill_use_case.execute(skill_id=skill_id)
        
        if not skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return json.loads(skill.model_dump_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@skill_router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str):
    try:
        skill_repository = SkillRepository()
        question_repository = QuestionRepository()
        delete_skill_use_case = DeleteSkillUseCase(skill_repository, question_repository)
        
        await delete_skill_use_case.execute(skill_id=skill_id)
        
        return {"detail": "Skill deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@skill_router.patch("/", response_model=Skill)
async def update_skill( skill: Skill):
    try:
        skill_repository = SkillRepository()
        update_skill_use_case = UpdateSkillUseCase(skill_repository)
        

        updated_skill = await update_skill_use_case.execute(skill_data=skill)

        return json.loads(updated_skill.model_dump_json())

        
        
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
      
   






