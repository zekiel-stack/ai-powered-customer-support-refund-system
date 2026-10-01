import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai import classify_issue
from database import connect_db, initialize_db
from policy import decide_refund

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header



logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

initialize_db()
app = FastAPI(title="Refund Support API")


class OrderLookupInput(BaseModel): #class for order lookup input
    email: str
    order_id: str



class RefundInput(BaseModel): #class for refund input
    email: str
    order_id: str
    message: str = Field(min_length=10, max_length=1000)


@app.get("/status")
def health():
    return {"status": "ok"}

#endpoint for submitting refund request
@app.post("/api/refunds")
def submit_refund(request: RefundInput):
    connection = connect_db()

    try:
        order = connection.execute(
            """
            SELECT o.id, o.item, o.amount, o.purchase_date, o.final_sale
            FROM orders AS o
            JOIN customers AS c ON o.customer_id = c.id
            WHERE o.id = ? AND LOWER(c.email) = LOWER(?)
            """,
            (request.order_id.strip(), request.email.strip()),
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="No order matches those details.",
            )

        try:
            issue = classify_issue(request.message)
            ai_failed = False
        except Exception:
            logger.exception("AI classification failed")
            issue = "unclear"
            ai_failed = True

        result = decide_refund(dict(order), issue)

        if ai_failed:
            result["reason"] = (
                "AI classification was unavailable, so a support agent "
                "will review this request."
            )

        cursor = connection.execute(
            """
            INSERT INTO refund_requests
                (order_id, message, issue, decision, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                order["id"],
                request.message,
                issue,
                result["decision"],
                result["reason"],
            ),
        )
        connection.commit()

        return {
            "request_id": cursor.lastrowid,
            "order_id": order["id"],
            "item": order["item"],
            "issue": issue,
            "decision": result["decision"],
            "reason": result["reason"],
        }
    finally:
        connection.close()


#Admin endpoint for all refund request 
@app.get("/api/admin/refunds")
def list_refund_requests(x_admin_token: str | None = Header(default=None)):
    expected_token = os.getenv("ADMIN_TOKEN")

    if (
        not expected_token
        or not x_admin_token
        or not secrets.compare_digest(x_admin_token, expected_token)
    ):
        raise HTTPException(status_code=403, detail="Admin access required.")

    connection = connect_db()
    try:
        rows = connection.execute(
            """
            SELECT
                r.id AS request_id,
                r.order_id,
                c.name AS customer_name,
                c.email,
                o.item,
                o.amount,
                r.message,
                r.issue,
                r.decision,
                r.reason
            FROM refund_requests AS r
            JOIN orders AS o ON r.order_id = o.id
            JOIN customers AS c ON o.customer_id = c.id
            ORDER BY r.id DESC
            """
        ).fetchall()

        return {"requests": [dict(row) for row in rows]}
    finally:
        connection.close()


#endpoint for look up order with email and order id 
@app.post("/api/orders/lookup")
def lookup_order(request: OrderLookupInput):
    connection = connect_db()
    try:
        order = connection.execute(
            """
            SELECT o.id, o.item, o.amount, o.purchase_date, o.final_sale
            FROM orders AS o
            JOIN customers AS c ON o.customer_id = c.id
            WHERE o.id = ? AND LOWER(c.email) = LOWER(?)
            """,
            (request.order_id.strip(), request.email.strip()),
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="No order matches those details.",
            )

        return {
            "order_id": order["id"],
            "item": order["item"],
            "amount": order["amount"],
            "purchase_date": order["purchase_date"],
            "final_sale": bool(order["final_sale"]),
        }
    finally:
        connection.close()