from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

AGENT_URL = "http://agent:4242/respond"


class ChatRequest(BaseModel):
    message: str
    mode: str = "chat"   # chat / builder
    user_id: str = "user_1"


@app.get("/")
def root():
    return {"status": "Multi-AI system running"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        user_message = req.message

        # 🔥 BUILDER MODE
        if req.mode == "builder":
            prompt = f"""
You are an advanced AI builder.
User request: {user_message}

Generate:
- Full system / app / code
- Step-by-step
- Production ready
"""
        else:
            # 🌍 MULTI LANGUAGE CHAT MODE
            prompt = f"""
User said: {user_message}
Respond naturally in same language.
"""

        payload = {
            "utterance": prompt,
            "user_id": req.user_id
        }

        response = requests.post(AGENT_URL, json=payload, timeout=20)

        if response.status_code != 200:
            return {"error": "Agent error"}

        data = response.json()

        reply = data.get("response")

        if not reply and "hypotheses" in data:
            reply = data["hypotheses"][0].get("text")

        return {
            "reply": reply
        }

    except Exception as e:
        return {"error": str(e)}
