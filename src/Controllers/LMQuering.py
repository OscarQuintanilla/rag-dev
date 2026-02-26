import os
from dotenv import load_dotenv
# SRP History
from ..Utils.ChatUtils import add_message_to_history
from ..Utils.ChatUtils import history_init
# SRP RAG
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from openai import OpenAI

load_dotenv()

# Initialize vector store once at module level (singleton pattern)
_embedding_function = OllamaEmbeddings(model='nomic-embed-text')
# Resolve absolute path for VDB to avoid CWD issues
base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
vdb_relative = os.getenv('VDB_ACCESS_PATH', './VDB/CAMPESTREVDB')
# Clean up the relative path if it starts with ./
if vdb_relative.startswith('./'):
    vdb_relative = vdb_relative[2:]
    
persist_directory = os.path.join(base_path, vdb_relative)

print(f"📂 Loading Vector Store from: {persist_directory}")

_vectorstore = Chroma(
    collection_name=os.getenv('COLLECTION_VDB_NAME'),
    persist_directory=persist_directory,
    embedding_function=_embedding_function
)

# Sends a message to the LLM server and returns the response
def chat_to_llm_server(message):    
    history = history_init()

    # Perform semantic search using the singleton vectorstore
    print(f"🔍 Searching for: {message}")
    semantic_search = _vectorstore.similarity_search(f"ENTITY: {message}", k=10)
    print(f"📄 Found {len(semantic_search)} documents")

    context_parts = [doc.page_content for doc in semantic_search]
    context = "\n\n---\n\n".join(context_parts)

    # Build the RAG prompt with context
    user_message = f"""
Eres un asistente que genera consultas SQL Server (T-SQL).

REGLAS:
- Usa exclusivamente el esquema proporcionado.
- No inventes tablas, columnas ni schemas.
- Usa solo SELECT.
- Si la información no es suficiente, responde exactamente:
  "No puedo generar esta consulta con el esquema proporcionado."
- Responde únicamente con la consulta SQL, sin explicaciones adicionales. NO agregues caracteres como ", ', etc. Solo la consulta SQL lista para ejecutar.
- Si existe una tabla cuyo nombre coincide exactamente con la entidad preguntada,
  esa tabla debe considerarse la fuente principal.
- Si existe una tabla llamada "Dealer", úsala para contar dealers.
- Columnas con el mismo nombre en otras tablas NO definen la entidad.
- Si hay una tabla llamada "Dealer", úsala para contar dealers.
- SIEMPRE usa un ALIAS (AS) claro para cada columna seleccionada, usando snake_case por ejemplo: "SELECT COUNT(*) AS total_ventas".

Si no existe una tabla que defina claramente la entidad,
responde que la información es insuficiente.

CONTEXTO (ESQUEMA):
{context}

PREGUNTA DEL USUARIO:
{message}
"""


    add_message_to_history(history, 'user', user_message)
    
    # Request the LLM server
    # llm_client = OpenAI(base_url=os.getenv('LLM_SERVER_URL'), api_key='not-needed')
    # querying_server = llm_client.chat.completions.create(
    #     model='local-model',
    #     messages=history,
    #     temperature=0.1,
    #     stream=False
    # )

    from anthropic import Anthropic

    client = Anthropic()  # Lee ANTHROPIC_API_KEY del entorno

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=history
    )
    print(message.content)

    # Extract the assistant's response
    # llm_response = querying_server.choices[0].message.content
    llm_response = message.content[0].text
    add_message_to_history(history, 'assistant', llm_response)
    
    object_response = {
        "content": llm_response,
        "history": history,
        "context": context
    }


    return object_response
