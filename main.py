from fastapi import FastAPI
from pydantic import BaseModel
import stripe
import os

app = FastAPI()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
PRICE_ID = os.getenv("STRIPE_METERED_PRICE_ID")

class CustomerRequest(BaseModel):
    email: str

class SubscriptionRequest(BaseModel):
    customer_id: str

class UsageRequest(BaseModel):
    subscription_id: str
    units: int

@app.post("/create-customer")
def create_customer(req: CustomerRequest):
    customer = stripe.Customer.create(email=req.email)
    return {"customer_id": customer.id}

@app.post("/create-subscription")
def create_subscription(req: SubscriptionRequest):
    subscription = stripe.Subscription.create(
        customer=req.customer_id,
        items=[{"price": PRICE_ID}]
    )
    return {"subscription_id": subscription.id}

@app.post("/report-usage")
def report_usage(req: UsageRequest):
    subscription_item = stripe.Subscription.retrieve(req.subscription_id).items.data[0].id
    usage_record = stripe.UsageRecord.create(
        subscription_item=subscription_item,
        quantity=req.units,
        action="increment"
    )
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
