from datetime import datetime, timezone
from app.email.schemas import EmailIn, ParsedEmailOut, ActionItemOut
from app.ai.schemas import ParsedEmailResult


class DemoStore:
    def __init__(self) -> None:
        self._emails: list[ParsedEmailOut] = []
        self._actions: list[ActionItemOut] = []
        self._next_email_id = 1
        self._next_action_id = 1

    def add_email(self, email: EmailIn, parsed: ParsedEmailResult) -> ParsedEmailOut:
        extracted = dict(parsed.extracted)
        extracted["_meta"] = {
            "parser_used": parsed.parser_used,
            "ai_escalated": parsed.ai_escalated,
            "escalation_reason": parsed.escalation_reason,
        }

        item = ParsedEmailOut(
            id=self._next_email_id,
            sender=email.sender,
            subject=email.subject,
            category=parsed.classification.category.value,
            confidence=parsed.classification.confidence,
            extracted=extracted,
            created_at=datetime.now(timezone.utc),
        )
        self._next_email_id += 1
        self._emails.append(item)
        self.add_action(item)
        return item

    def add_action(self, email: ParsedEmailOut) -> ActionItemOut:
        title_map = {
            "supplier_offer": "Review supplier offer",
            "customer_order": "Draft customer confirmation",
            "shipping_notice": "Match shipment to PO",
            "complaint": "Flag quality issue",
            "general": "Human review needed",
        }
        priority_map = {
            "supplier_offer": "normal",
            "customer_order": "high",
            "shipping_notice": "normal",
            "complaint": "urgent",
            "general": "low",
        }

        extracted = email.extracted
        action = ActionItemOut(
            id=self._next_action_id,
            parsed_email_id=email.id,
            title=title_map.get(email.category, "Review email"),
            detail=extracted.get("suggested_action", "Review parsed email and decide next step."),
            status="open",
            priority=priority_map.get(email.category, "normal"),
            created_at=datetime.now(timezone.utc),
        )
        self._next_action_id += 1
        self._actions.append(action)
        return action

    def list_emails(self) -> list[ParsedEmailOut]:
        return list(reversed(self._emails))

    def list_actions(self) -> list[ActionItemOut]:
        return list(reversed(self._actions))

    def clear(self) -> None:
        self._emails.clear()
        self._actions.clear()
        self._next_email_id = 1
        self._next_action_id = 1


demo_store = DemoStore()
