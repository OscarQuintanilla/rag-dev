from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel

from src.Controllers.LMQuering import chat_to_llm_server, infer_views_from_query
from src.Controllers.SQLController import execute_sql_from_request

class UserMessage(BaseModel):
    message: str
    history: list = []

class SQLRequest(BaseModel):
    query: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/test")
def confirm_test():
    return {"working": "true"}

@app.post("/api/chat")
def send_message(req: UserMessage):
    object_response = chat_to_llm_server(req.message, req.history)
    return object_response

@app.post("/api/infer-views")
def infer_views(req: UserMessage):
    object_response = infer_views_from_query(req.message)
    return object_response

@app.post("/api/execute-sql")
def execute_sql(req: SQLRequest):
    data = execute_sql_from_request(req.query)
    # Check for error
    if isinstance(data, dict) and "error" in data:
        return {"table_data": [], "error": data["error"]}
    # Ensure we return a structured response
    return {"table_data": data}
