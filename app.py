from fastapi import FastAPI, Request, Header, HTTPException
import httpx, os

app = FastAPI()
RELAY_SECRET = os.getenv("RELAY_SECRET")
OPENAI_KEY   = os.getenv("OPENAI_API_KEY")

@app.post("/v1/chat/completions")
async def relay(request: Request, x_relay_secret: str | None = Header(None)):
    if RELAY_SECRET and x_relay_secret != RELAY_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    body = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as c:
        r = await c.post(
            "https://api.openai.com/v1/chat/completions",
            json=body,
            headers={"Authorization": f"Bearer {OPENAI_KEY}"}
        )
    return r.json()
