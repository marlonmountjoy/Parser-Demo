from pydantic import BaseModel
from app.email.schemas import EmailIn


class DemoScenario(BaseModel):
    id: str
    title: str
    subtitle: str
    business_value: str
    email: EmailIn


SCENARIOS = [
    DemoScenario(
        id="supplier-offer",
        title="Supplier Offer",
        subtitle="Inbound availability and pricing",
        business_value="Turns supplier availability emails into structured purchase opportunities.",
        email=EmailIn(
            sender="sales@northcoastseafood.com",
            subject="Black Cod available this week",
            body="Fresh H&G black cod available FOB Seattle. 5,000 lbs total, 12-15 lb size, packed in 50 lb boxes. Price is $8.90/lb, net 14.",
        ),
    ),
    DemoScenario(
        id="customer-order",
        title="Customer Order",
        subtitle="Freeform customer request",
        business_value="Extracts order details and suggests a customer confirmation workflow.",
        email=EmailIn(
            sender="buyer@anchorrestaurant.com",
            subject="Order for Friday",
            body="Can you ship 8 cases of King Salmon fillet for Friday? Same delivery address as usual. Please confirm price.",
        ),
    ),
    DemoScenario(
        id="shipping-notice",
        title="Shipping Notice",
        subtitle="Warehouse or carrier update",
        business_value="Pulls ETA, carrier, tracking, PO, and product details from logistics messages.",
        email=EmailIn(
            sender="warehouse@example.com",
            subject="PO-1042 shipped",
            body="PO 1042 shipped today via Old Dominion. BOL: OD998812. ETA Friday. 1,980 lbs King Salmon.",
        ),
    ),
    DemoScenario(
        id="quality-complaint",
        title="Quality Complaint",
        subtitle="Customer issue / recall risk",
        business_value="Flags quality issues immediately and ties complaints back to lot/product details.",
        email=EmailIn(
            sender="buyer@example.com",
            subject="Quality issue lot OCS-20260517-0001",
            body="The black cod from lot OCS-20260517-0001 had a bad smell on arrival. Please call me. We need credit or replacement.",
        ),
    ),
    DemoScenario(
        id="ambiguous",
        title="Ambiguous Email",
        subtitle="Low-confidence case",
        business_value="Shows why hybrid AI escalation matters when rules are not confident.",
        email=EmailIn(
            sender="pete@example.com",
            subject="Question",
            body="Can you look at the fish thing we talked about and let me know what makes sense?",
        ),
    ),
]
