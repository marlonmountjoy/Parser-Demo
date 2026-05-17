from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EmailCategory(str, Enum):
    supplier_offer = "supplier_offer"
    customer_order = "customer_order"
    shipping_notice = "shipping_notice"
    complaint = "complaint"
    general = "general"


class EmailClassification(BaseModel):
    category: EmailCategory
    confidence: float = Field(default=0.80, ge=0.0, le=1.0)
    reason: str


class OfferedProduct(BaseModel):
    species_common_name: str
    species_scientific_name: Optional[str] = None
    form: Optional[str] = None
    size_grade: Optional[str] = None
    pack_size: Optional[str] = None
    origin: Optional[str] = None
    quantity_lbs: Optional[float] = None
    price_per_lb: Optional[float] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class SupplierOffer(BaseModel):
    supplier_name: Optional[str] = None
    supplier_email: Optional[str] = None
    products: list[OfferedProduct] = []
    terms: Optional[str] = None
    valid_until: Optional[str] = None
    suggested_action: str = "Create purchase review"


class CustomerOrderLine(BaseModel):
    species_common_name: str
    form: Optional[str] = None
    quantity_cases: Optional[int] = None
    quantity_lbs: Optional[float] = None
    requested_delivery_date: Optional[str] = None
    notes: Optional[str] = None


class CustomerOrder(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    lines: list[CustomerOrderLine] = []
    requested_ship_date: Optional[str] = None
    requested_delivery_date: Optional[str] = None
    suggested_action: str = "Draft customer confirmation"


class ShippingNotice(BaseModel):
    sender_name: Optional[str] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    eta: Optional[str] = None
    products: list[OfferedProduct] = []
    related_po_number: Optional[str] = None
    suggested_action: str = "Match shipment to purchase order"


class Complaint(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    issue_type: Optional[str] = None
    severity: str = "needs_review"
    product: Optional[str] = None
    lot_number: Optional[str] = None
    details: Optional[str] = None
    suggested_action: str = "Flag quality issue for review"


class ParsedEmailResult(BaseModel):
    classification: EmailClassification
    extracted: dict
    parser_used: str = "rules"
    ai_escalated: bool = False
    escalation_reason: str | None = None
