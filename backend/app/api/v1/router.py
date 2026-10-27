from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    auth,
    competency,
    courses,
    gamification,
    learning_path,
    materials,
    notifications,
    quiz,
    tutor,
    wellness,
    career_stage,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(courses.router)
api_router.include_router(competency.router)
api_router.include_router(quiz.router)
api_router.include_router(career_stage.router)
api_router.include_router(learning_path.router)
api_router.include_router(materials.router)
api_router.include_router(gamification.router)
api_router.include_router(notifications.router)
api_router.include_router(analytics.router)
api_router.include_router(tutor.router)
api_router.include_router(wellness.router)

