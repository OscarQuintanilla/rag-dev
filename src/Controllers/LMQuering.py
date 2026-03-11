import os
from dotenv import load_dotenv
# SRP History
from ..Utils.ChatUtils import add_message_to_history
from ..Utils.ChatUtils import history_init
from ..Utils.HybridSearch import hybrid_search
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
    semantic_search = hybrid_search(_vectorstore, message, k=10)
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
- Responde únicamente con la consulta SQL pura, sin explicaciones adicionales y SIN usar formato de bloque de código Markdown (```sql ... ```). Devuelve solo texto plano.
- Si existe una tabla cuyo nombre coincide exactamente con la entidad preguntada,
  esa tabla debe considerarse la fuente principal.
- Si NO existe una tabla con el nombre de la entidad, pero sí existe una columna
  con ese nombre en alguna tabla, usa COUNT(DISTINCT [columna]) para contar entidades únicas.
- SIEMPRE usa un ALIAS (AS) claro para cada columna seleccionada en snake_case.
  Ejemplo: SELECT COUNT(DISTINCT Dealer) AS total_dealers

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
    
    # Limpiar formato markdown (```sql) si el modelo insiste en agregarlo
    llm_response = llm_response.strip()
    if llm_response.startswith('```sql'):
        llm_response = llm_response[6:]
    elif llm_response.startswith('```'):
        llm_response = llm_response[3:]
    if llm_response.endswith('```'):
        llm_response = llm_response[:-3]
    llm_response = llm_response.strip()

    add_message_to_history(history, 'assistant', llm_response)
    
    object_response = {
        "content": llm_response,
        "history": history,
        "context": context
    }


    return object_response


# Infers which database views/tables best match the user's request
def infer_views_from_query(message):
    history = history_init()

    # Perform semantic search using the singleton vectorstore
    print(f"🔍 [ViewInfer] Searching for: {message}")
    semantic_search = hybrid_search(_vectorstore, message, k=15)
    print(f"📄 [ViewInfer] Found {len(semantic_search)} documents")

    context_parts = [doc.page_content for doc in semantic_search]
    context = "\n\n---\n\n".join(context_parts)

    # Build the prompt with rules oriented to view/table inference
    user_message = f"""
Eres un asistente experto en bases de datos SQL Server.

TU OBJETIVO:
Analizar la solicitud del usuario y generar una consulta SQL llamando a la vista o tabla de la base de datos
que mejor se adecúe para obtener la información que solicita el usuario.

REGLAS:
- Usa exclusivamente las vistas y tablas proporcionadas en el contexto.
- No inventes tablas, vistas, columnas ni esquemas que no existan en el contexto.
- Genera ÚNICAMENTE la consulta SQL en texto plano, sin explicaciones adicionales y SIN el bloque de código Markdown (```sql ... ```).
- Asegúrate de seleccionar la vista más relevante y que la consulta extraiga los datos tal como los solicita el usuario (usa SELECT, WHERE, GROUP BY, etc., según corresponda).
- Si ninguna tabla/vista se ajusta a la solicitud, responde exactamente:
  "No se encontraron vistas o tablas que se ajusten a la solicitud para generar la consulta."
- Responde en español.
- Sé conciso y preciso.

CONTEXTO (ESQUEMA DISPONIBLE):
{context}

SOLICITUD DEL USUARIO:
{message}
"""

    add_message_to_history(history, 'user', user_message)

    from anthropic import Anthropic

    client = Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2500,
        messages=history
    )
    print(response.content)

    llm_response = response.content[0].text
    
    # Limpiar formato markdown (```sql) si el modelo insiste en agregarlo
    llm_response = llm_response.strip()
    if llm_response.startswith('```sql'):
        llm_response = llm_response[6:]
    elif llm_response.startswith('```'):
        llm_response = llm_response[3:]
    if llm_response.endswith('```'):
        llm_response = llm_response[:-3]
    llm_response = llm_response.strip()

    add_message_to_history(history, 'assistant', llm_response)

    object_response = {
        "content": llm_response,
        "history": history,
        "context": context
    }

    return object_response
