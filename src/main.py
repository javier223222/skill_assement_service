from fastapi import FastAPI
from contextlib import asynccontextmanager

from infrastructure.database.mongo_connection import mongo_connection

from domain.entities.skill import Skill
from presentation.api.skill_controller import skill_router
from presentation.api.assement_controller import assement_router


from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_connection.connect()
    yield
    
    await mongo_connection.disconnect()
app = FastAPI(
    title="Skill Assentment Service",
    description="Microservicio para evaluación de habilidades técnicas con IA",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(
    router=skill_router,
    prefix="/api/v1",
    
)
app.include_router(
    router=assement_router,
    prefix="/api/v1",
)
@app.get("/")
async def health_check():
    """Endpoint básico de health check"""
    return {
        "status": "ok",
        "service": "skill-assessment-service",
        "message": "Servicio funcionando correctamente"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8002, reload=True)


    