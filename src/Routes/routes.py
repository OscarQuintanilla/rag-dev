from fastapi import APIRouter
import logging
from pydantic import BaseModel

from src.Controllers.LMQuering import send_to_llm

class UserMessage(BaseModel):
    message: str

app = APIRouter()

@app.get("/api/test")
def confirm_test():
    return {"working": "true"}

@app.post("/api/chat")
def send_message(req: UserMessage):
    llm_response = send_to_llm(req.message)

    return {"response": llm_response.get('choices', [{}])[0].get('message', {}).get('content', '')}
