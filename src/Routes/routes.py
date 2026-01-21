from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel

from src.Controllers.LMQuering import chat_to_llm_server

class UserMessage(BaseModel):
    message: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
def confirm_test():
    return {"working": "true"}

@app.post("/api/chat")
def send_message(req: UserMessage):
    object_response = chat_to_llm_server(req.message)
    return object_response
