from app.core.config import settings
from app.ai.providers.base import AIProvider
from app.ai.providers.mock import MockAIProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.hybrid import HybridAIProvider


def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "mock":
        return MockAIProvider()

    if settings.ai_provider == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key or "", model=settings.gemini_model)

    if settings.ai_provider == "hybrid":
        return HybridAIProvider(
            rule_provider=MockAIProvider(),
            fallback_provider=GeminiProvider(api_key=settings.gemini_api_key or "", model=settings.gemini_model),
            threshold=settings.ai_escalation_threshold,
        )

    raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
