from abc import ABC, abstractmethod
from app.email.schemas import EmailIn
from app.ai.schemas import ParsedEmailResult


class AIProvider(ABC):
    @abstractmethod
    async def parse_email(self, email: EmailIn) -> ParsedEmailResult:
        raise NotImplementedError
