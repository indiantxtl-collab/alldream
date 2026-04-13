from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

AGENT_URL = "http://agent:4242/respond"


class ChatRequest(BaseModel):
    message: str
    user_id: str = "user_1"


@app.get("/")
def root():
    return {"status": "AI system running"}


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        payload = {
            "utterance": req.message,
            "user_id": req.user_id
        }

        response = requests.post(AGENT_URL, json=payload, timeout=15)

        if response.status_code != 200:
            return {
                "error": "Agent not responding",
                "status_code": response.status_code
            }

        data = response.json()

        # 🔥 DeepPavlov response handling (multi-layer safe parsing)
        reply = None

        # Case 1: direct response
        if isinstance(data, dict):
            reply = data.get("response")

        # Case 2: hypotheses (skills output)
        if not reply and isinstance(data, dict):
            hypotheses = data.get("hypotheses")
            if hypotheses and isinstance(hypotheses, list):
                reply = hypotheses[0].get("text") if isinstance(hypotheses[0], dict) else None

        # Case 3: fallback
        if not reply:
            reply = "AI couldn't generate a proper response."

        return {
            "reply": reply,
            "raw": data  # debug ke liye (future me hata sakta hai)
        }

    except Exception as e:
        return {
            "error": str(e)
      }
