from app.ai.providers.base import AIProvider
from app.ai.schemas import ParsedEmailResult
from app.email.schemas import EmailIn


class HybridAIProvider(AIProvider):
    def __init__(self, rule_provider: AIProvider, fallback_provider: AIProvider, threshold: float = 0.85):
        self.rule_provider = rule_provider
        self.fallback_provider = fallback_provider
        self.threshold = threshold

    async def parse_email(self, email: EmailIn) -> ParsedEmailResult:
        rule_result = await self.rule_provider.parse_email(email)
        confidence = rule_result.classification.confidence

        if confidence >= self.threshold:
            rule_result.parser_used = "rules"
            rule_result.ai_escalated = False
            return rule_result

        ai_result = await self.fallback_provider.parse_email(email)
        ai_result.parser_used = "gemini"
        ai_result.ai_escalated = True
        ai_result.escalation_reason = f"Rule confidence {confidence:.2f} was below threshold {self.threshold:.2f}."
        return ai_result
