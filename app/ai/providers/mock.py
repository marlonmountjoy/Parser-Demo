import re
from app.ai.providers.base import AIProvider
from app.email.schemas import EmailIn
from app.ai.schemas import (
    EmailCategory, EmailClassification, ParsedEmailResult, SupplierOffer,
    OfferedProduct, CustomerOrder, CustomerOrderLine, ShippingNotice, Complaint
)


def _find_number_before(text: str, words: list[str]) -> float | None:
    for word in words:
        match = re.search(rf"(\d+(?:,\d{{3}})*(?:\.\d+)?)\s*{word}", text, flags=re.I)
        if match:
            return float(match.group(1).replace(",", ""))
    return None


def _find_price(text: str) -> float | None:
    match = re.search(r"\$(\d+(?:\.\d{1,2})?)\s*/\s*(?:lb|pound)", text, flags=re.I)
    return float(match.group(1)) if match else None


def _detect_species(text: str) -> str:
    species = ["king salmon", "coho salmon", "black cod", "sablefish", "halibut", "dungeness crab", "rockfish", "ling cod", "albacore", "shrimp", "oysters", "branzino"]
    lowered = text.lower()
    for item in species:
        if item in lowered:
            return item.title()
    return "Unknown Seafood Product"


class MockAIProvider(AIProvider):
    async def parse_email(self, email: EmailIn) -> ParsedEmailResult:
        text = f"{email.subject}\n{email.body}".lower()

        if any(word in text for word in ["quality", "complaint", "spoiled", "bad smell", "illness", "credit", "replacement"]):
            return self._complaint(email)
        if any(word in text for word in ["shipped", "tracking", "eta", "carrier", "bol"]):
            return self._shipping_notice(email)
        if any(word in text for word in ["need", "order", "please send", "can you ship", "for friday"]):
            return self._customer_order(email)
        if any(word in text for word in ["available", "offer", "fob", "fresh", "frozen", "price"]):
            return self._supplier_offer(email)

        return ParsedEmailResult(
            classification=EmailClassification(category=EmailCategory.general, confidence=0.45, reason="No strong operational pattern detected."),
            extracted={"suggested_action": "Needs human review"},
            parser_used="rules",
        )

    def _supplier_offer(self, email: EmailIn) -> ParsedEmailResult:
        full_text = f"{email.subject}\n{email.body}"
        product = OfferedProduct(
            species_common_name=_detect_species(full_text),
            form="H&G" if "h&g" in full_text.lower() else ("fillet" if "fillet" in full_text.lower() else None),
            size_grade=self._detect_size_grade(full_text),
            pack_size=self._detect_pack_size(full_text),
            origin=self._detect_origin(full_text),
            quantity_lbs=_find_number_before(full_text, ["lbs", "lb", "pounds"]),
            price_per_lb=_find_price(full_text),
            location=self._detect_location(full_text),
            notes="Review supplier availability before purchasing.",
        )
        confidence = 0.55
        for value in [product.species_common_name != "Unknown Seafood Product", product.quantity_lbs, product.price_per_lb, product.location]:
            if value:
                confidence += 0.09
        data = SupplierOffer(supplier_name=self._sender_name(email.sender), supplier_email=email.sender, products=[product], terms=self._detect_terms(full_text))
        return ParsedEmailResult(
            classification=EmailClassification(category=EmailCategory.supplier_offer, confidence=min(confidence, 0.91), reason="Supplier availability/pricing pattern detected."),
            extracted=data.model_dump(),
            parser_used="rules",
        )

    def _customer_order(self, email: EmailIn) -> ParsedEmailResult:
        full_text = f"{email.subject}\n{email.body}"
        line = CustomerOrderLine(
            species_common_name=_detect_species(full_text),
            form="fillet" if "fillet" in full_text.lower() else None,
            quantity_cases=int(_find_number_before(full_text, ["cases", "case"]) or 0) or None,
            quantity_lbs=_find_number_before(full_text, ["lbs", "lb", "pounds"]),
            requested_delivery_date=self._detect_date_phrase(full_text),
            notes="Confirm inventory before replying.",
        )
        confidence = 0.55
        for value in [line.species_common_name != "Unknown Seafood Product", line.quantity_cases or line.quantity_lbs, line.requested_delivery_date]:
            if value:
                confidence += 0.10
        data = CustomerOrder(customer_name=self._sender_name(email.sender), customer_email=email.sender, lines=[line], requested_delivery_date=self._detect_date_phrase(full_text))
        return ParsedEmailResult(
            classification=EmailClassification(category=EmailCategory.customer_order, confidence=min(confidence, 0.88), reason="Customer order/request pattern detected."),
            extracted=data.model_dump(),
            parser_used="rules",
        )

    def _shipping_notice(self, email: EmailIn) -> ParsedEmailResult:
        full_text = f"{email.subject}\n{email.body}"
        tracking = re.search(r"(?:tracking|pro|bol)[ #:]*([A-Z0-9-]+)", full_text, flags=re.I)
        data = ShippingNotice(
            sender_name=self._sender_name(email.sender),
            carrier=self._detect_carrier(full_text),
            tracking_number=tracking.group(1) if tracking else None,
            eta=self._detect_date_phrase(full_text),
            related_po_number=self._detect_po(full_text),
            products=[OfferedProduct(species_common_name=_detect_species(full_text), quantity_lbs=_find_number_before(full_text, ["lbs", "lb", "pounds"]))],
        )
        return ParsedEmailResult(
            classification=EmailClassification(category=EmailCategory.shipping_notice, confidence=0.80, reason="Shipment status pattern detected."),
            extracted=data.model_dump(),
            parser_used="rules",
        )

    def _complaint(self, email: EmailIn) -> ParsedEmailResult:
        full_text = f"{email.subject}\n{email.body}"
        data = Complaint(
            customer_name=self._sender_name(email.sender),
            customer_email=email.sender,
            issue_type="quality_issue",
            severity="high" if any(w in full_text.lower() for w in ["illness", "sick", "spoiled"]) else "needs_review",
            product=_detect_species(full_text),
            lot_number=self._detect_lot(full_text),
            details=email.body,
        )
        return ParsedEmailResult(
            classification=EmailClassification(category=EmailCategory.complaint, confidence=0.88, reason="Quality or complaint pattern detected."),
            extracted=data.model_dump(),
            parser_used="rules",
        )

    def _sender_name(self, sender: str) -> str:
        return sender.split("@")[0].replace(".", " ").replace("_", " ").title()

    def _detect_origin(self, text: str) -> str | None:
        for origin in ["Alaska", "Oregon", "Washington", "Mexico", "Ecuador", "Canada", "Chile"]:
            if origin.lower() in text.lower():
                return origin
        return None

    def _detect_location(self, text: str) -> str | None:
        for location in ["Tigard", "Seattle", "San Francisco", "Pier 45", "Los Angeles", "LA"]:
            if location.lower() in text.lower():
                return location
        return None

    def _detect_size_grade(self, text: str) -> str | None:
        match = re.search(r"(\d+\s*-\s*\d+\s*lb|\d+/\d+|\d+\s*oz)", text, flags=re.I)
        return match.group(1) if match else None

    def _detect_pack_size(self, text: str) -> str | None:
        match = re.search(r"(\d+\s*lb\s*(?:box|boxes|case|cases|cs|master))", text, flags=re.I)
        return match.group(1) if match else None

    def _detect_terms(self, text: str) -> str | None:
        match = re.search(r"(net\s*\d+|cod|prepaid|fob\s+\w+)", text, flags=re.I)
        return match.group(1) if match else None

    def _detect_date_phrase(self, text: str) -> str | None:
        for phrase in ["today", "tomorrow", "friday", "monday", "tuesday", "wednesday", "thursday"]:
            if phrase in text.lower():
                return phrase
        return None

    def _detect_carrier(self, text: str) -> str | None:
        for carrier in ["FedEx", "UPS", "DHL", "Old Dominion", "XPO", "Lineage"]:
            if carrier.lower() in text.lower():
                return carrier
        return None

    def _detect_po(self, text: str) -> str | None:
        match = re.search(r"PO[- #:]*(\d+)", text, flags=re.I)
        return f"PO-{match.group(1)}" if match else None

    def _detect_lot(self, text: str) -> str | None:
        match = re.search(r"lot[- #:]*([A-Z0-9-]+)", text, flags=re.I)
        return match.group(1) if match else None
