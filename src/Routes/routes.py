from fastapi import APIRouter
import logging
from pydantic import BaseModel

from src.Controllers.LMQuering import chat_to_llm_server

class UserMessage(BaseModel):
    message: str

app = APIRouter()

@app.get("/api/test")
def confirm_test():
    return {"working": "true"}

@app.post("/api/chat")
def send_message(req: UserMessage):
    object_response = chat_to_llm_server(req.message)
    return object_response
