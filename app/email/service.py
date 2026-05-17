from app.ai.providers.base import AIProvider
from app.email.schemas import EmailIn, ParsedEmailOut
from app.email.store import demo_store


class EmailParsingService:
    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    async def parse(self, email: EmailIn) -> ParsedEmailOut:
        parsed = await self.ai_provider.parse_email(email)
        return demo_store.add_email(email=email, parsed=parsed)
