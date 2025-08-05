from fastapi import FastAPI
from app.api.v1 import quotes
from api.models import User
app = FastAPI(title="Group Benefits Quote API")
app.include_router(quotes.router)
#

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}