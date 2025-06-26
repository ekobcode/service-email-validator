from fastapi import FastAPI, Request, Depends
from middleware.auth import api_key_auth
from services.email_validator import validate_email_address
import time

app = FastAPI(title="Advanced Email Validator API")


@app.get("/validate-email")
async def validate(email: str, request: Request, api_key: str = Depends(api_key_auth)):
    start_time = time.time()
    result = validate_email_address(email)
    response_time_ms = int((time.time() - start_time) * 1000)

    print(f"[EMAIL VALIDATION] IP: {request.client.host} | Email: {email} | Status: {result['status']} | Message: {result['message']} | ResponseTime: {response_time_ms}ms")

    return result

@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "message": "pong",
        "timestamp": int(time.time() * 1000)
    }