import requests
from src.Classes.LMStudioRequest import LMStudioRequest

def send_to_llm(message):
    request = LMStudioRequest(
        model="nombre-del-modelo",
        messages=[
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": message}
        ],
        temperature=0.7,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )

    payload = request.to_dict()
    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload)
    return response.json()