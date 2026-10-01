from datetime import date


def decide_refund(order: dict, issue: str) -> dict:
    if issue in ("suspicious", "unclear"):
        return {
            "decision": "Escalated",
            "reason": "A support agent needs to review this request.",
        }

    if order["final_sale"]:
        return {
            "decision": "Denied",
            "reason": "Final-sale items are not eligible for refunds.",
        }

    days_since_purchase = (
        date.today() - date.fromisoformat(order["purchase_date"])
    ).days

    if days_since_purchase > 30:
        return {
            "decision": "Denied",
            "reason": "The order is outside the 30-day refund window.",
        }

    if order["amount"] > 500:
        return {
            "decision": "Escalated",
            "reason": "Refunds over $500 require human review.",
        }

    if issue in ("damaged", "incorrect"):
        return {
            "decision": "Approved",
            "reason": "The order meets the refund policy requirements.",
        }

    return {
        "decision": "Denied",
        "reason": "The reported reason is not eligible under the refund policy.",
    }