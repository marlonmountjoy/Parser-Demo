from fastapi import FastAPI
from app.core.config import settings
from app.email.routes import router as email_router
from app.demo.routes import router as demo_router
from app.web.routes import router as web_router

app = FastAPI(title=settings.app_name)

app.include_router(email_router)
app.include_router(demo_router)
app.include_router(web_router)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "ai_provider": settings.ai_provider,
        "ai_escalation_threshold": settings.ai_escalation_threshold,
    }
