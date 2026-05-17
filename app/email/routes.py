from fastapi import APIRouter, Depends
from app.ai.providers.factory import get_ai_provider
from app.ai.providers.base import AIProvider
from app.email.schemas import EmailIn, ParsedEmailOut, ActionItemOut
from app.email.service import EmailParsingService
from app.email.store import demo_store
from app.demo.scenarios import SCENARIOS

router = APIRouter(prefix="/emails", tags=["emails"])


def get_email_service(ai_provider: AIProvider = Depends(get_ai_provider)) -> EmailParsingService:
    return EmailParsingService(ai_provider=ai_provider)


@router.post("/parse", response_model=ParsedEmailOut)
async def parse_email(email: EmailIn, service: EmailParsingService = Depends(get_email_service)) -> ParsedEmailOut:
    return await service.parse(email)


@router.post("/scenario/{scenario_id}", response_model=ParsedEmailOut)
async def parse_scenario(scenario_id: str, service: EmailParsingService = Depends(get_email_service)) -> ParsedEmailOut:
    scenario = next((s for s in SCENARIOS if s.id == scenario_id), None)
    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return await service.parse(scenario.email)


@router.get("/parsed", response_model=list[ParsedEmailOut])
async def list_parsed_emails() -> list[ParsedEmailOut]:
    return demo_store.list_emails()


@router.get("/actions", response_model=list[ActionItemOut])
async def list_actions() -> list[ActionItemOut]:
    return demo_store.list_actions()


@router.post("/clear")
async def clear_demo_store() -> dict:
    demo_store.clear()
    return {"status": "cleared"}
