import json
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
import requests

# URL de tu servidor de LMStudio
LMSTUDIO_URL = "http://127.0.0.1:1234"

# 1 Embed the chunks and store them in Chroma

# get a json file and put it into a list
with open('files/menu.json', 'r') as file:
    text = file.read()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_text(text)

# convert documents to embeddings and store them
print('Starting Embedding')
vectorestore = Chroma.from_documents(
    documents=chunks, 
    collection_name="rag_chroma",
    embedding=embeddings.ollama.OllamaEmbedding(model="nomic-embed-text")
)

retriver = vectorestore.as_retriever()

# apply RAG

print('Starting RAG')
rag_template="""Answer based only on the following context and always in spanish:
{context}
Question: {question}
"""
rag_template = ChatPromptTemplate.from_template(rag_template)

def lmstudio_generate(prompt):
    response = requests.post(LMSTUDIO_URL, json={"prompt": prompt})
    if response.status_code == 200:
        return response.json().get('response', '')
    else:
        raise Exception(f"Error en la respuesta del servidor: {response.status_code}")

rag_chain = (
    {"context": retriver, "question": RunnablePassthrough()}
    | rag_template
    | lmstudio_generate
    | StrOutputParser()
)

print(rag_chain.invoke('¿qué es el menú de pupusas?'))
