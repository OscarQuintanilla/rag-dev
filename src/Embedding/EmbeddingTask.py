import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from uuid import uuid4

load_dotenv()

# 1️⃣ Cargar documentos (1 archivo = 1 doc)
loader = DirectoryLoader(
    '../DBBSchemas/Embeddings',
    glob='**/*.txt'
)
docs = loader.load()

print(f"Documentos cargados: {len(docs)}")

# 2️⃣ Embeddings
embedding_function = OllamaEmbeddings(
    model='nomic-embed-text'
)

vectorstore = Chroma(
    embedding_function=embedding_function,
    collection_name=os.getenv('COLLECTION_VDB_NAME'),
    persist_directory=os.getenv('EMBEDDING_OUTPUT_PATH')
)

# 3️⃣ Insertar documentos
uuids = [str(uuid4()) for _ in docs]
vectorstore.add_documents(documents=docs, ids=uuids)
print(f"Chunks indexados: {vectorstore._collection.count()}")

