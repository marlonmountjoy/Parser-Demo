from fastapi import APIRouter
from app.demo.scenarios import SCENARIOS, DemoScenario

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/scenarios", response_model=list[DemoScenario])
async def list_scenarios() -> list[DemoScenario]:
    return SCENARIOS
