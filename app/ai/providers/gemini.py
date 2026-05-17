import json
from google import genai
from google.genai import types
from app.ai.providers.base import AIProvider
from app.ai.schemas import ParsedEmailResult, EmailClassification, EmailCategory
from app.email.schemas import EmailIn

SYSTEM_INSTRUCTIONS = """
You are an extraction engine for a wholesale seafood distributor.
Classify into: supplier_offer, customer_order, shipping_notice, complaint, or general.
Return ONLY valid JSON:
{"classification":{"category":"general","confidence":0.0,"reason":"..."}, "extracted":{}}
Use null when unclear. Do not invent values.
"""

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER is gemini or hybrid.")
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def parse_email(self, email: EmailIn) -> ParsedEmailResult:
        prompt = f"Sender: {email.sender}\\nSubject: {email.subject}\\n\\nBody:\\n{email.body}"
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTIONS, response_mime_type="application/json", temperature=0.0),
        )
        payload = json.loads(response.text or "{}")
        classification = payload.get("classification", {})
        return ParsedEmailResult(
            classification=EmailClassification(
                category=EmailCategory(classification.get("category", "general")),
                confidence=float(classification.get("confidence", 0.70)),
                reason=classification.get("reason", "Parsed by Gemini."),
            ),
            extracted=payload.get("extracted", {}),
            parser_used="gemini",
            ai_escalated=True,
            escalation_reason="AI provider parsed this email.",
        )
