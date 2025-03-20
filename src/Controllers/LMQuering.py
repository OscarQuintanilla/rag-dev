import os
from dotenv import load_dotenv
import requests
from src.Classes.LMStudioRequest import LMStudioRequest
# SRP History
from ..Utils.ChatUtils import add_message_to_history
from ..Utils.ChatUtils import history_init
# SRP RAG
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
from openai import OpenAI

load_dotenv()

def chat_to_llm_server(message):    
    history = history_init();

    # apply RAG todo:SRP
    embedding_function=OllamaEmbeddings(model='nomic-embed-text')
    vectorstore=Chroma(
        collection_name= os.getenv('COLLECTION_VDB_NAME'),
        persist_directory= os.getenv('VECTOR_DB_PATH'),
        embedding_function= embedding_function
    )

    context = ""
    semantic_search = vectorstore.similarity_search(message, k=4)
    for result in semantic_search:
        context += result.page_content + '\n\n'

    # todo: add the context to the prompt

    # todo: request the server
    llm_client = OpenAI(base_url=os.getenv('LLM_SERVER_URL'), api_key='not-needed')

    for result in semantic_search:
        context += result.page_content + "\n\n"

    rag_template = {'Contesta solo basado solo en el siguiente contexto: {context} Mensaje del usuario: {message}'}
    
    add_message_to_history(history, 'user', f'Contesta solo basado solo en el siguiente contexto: {context} Mensaje del usuario: {message}')
        
    querying_server = llm_client.chat.completions.create(
        model = 'local-model', # prob not needed
        messages = history,
        temperature= 0.7,
        stream= False
    )

    request = LMStudioRequest(
        model="nombre-del-modelo", # presumiblemente sin usar
        messages=history,
        temperature=0.7,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )

    payload = request.to_dict()
    llm_response = requests.post("http://127.0.0.1:1234/v1/chat/completions", json=payload)
    llm_response = llm_response.json()
    llm_response = llm_response.get('choices', [{}])[0].get('message', {}).get('content', '')
    object_response = {
        "content": querying_server.json(),
        "history": history
    }   




    # todo:SRP
    
    add_message_to_history(history, 'assistant', llm_response)


    return object_response
