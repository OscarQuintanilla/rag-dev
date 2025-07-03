import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from uuid import uuid4

load_dotenv()

# loaders = [PyPDFLoader('./pdfs/brain-gliomas-patient.pdf')]
# loaders = [JSONLoader('./files/menu.json', jq_schema='.')] #cargamos el archivo a procesar
loaders = [DirectoryLoader(os.getenv('FILES_TO_EMBED_PATH'), glob='**/*.txt')]
# leer .txt
# loaders = [TextLoader('./files/info.txt', ))]

docs = []
for file in loaders:
    docs.extend(file.load())


import spacy

# Carga el modelo de spaCy solo una vez
nlp = spacy.load("es_core_news_md")

texts = [doc.page_content for doc in docs]

def propositional_chunking_array(texts, max_sentences_per_chunk=3):
    """
    Aplica el chunking proposicional a una lista de textos.
    Devuelve una lista con todos los chunks generados.
    """
    all_chunks = []
    for text in texts:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        for i in range(0, len(sentences), max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i+max_sentences_per_chunk])
            all_chunks.append(chunk)
    return all_chunks

# Ejemplo de uso
texto_largo = "Aquí va tu texto largo que quieres indexar..."

# Divide en proposiciones/chunks
chunks = propositional_chunking_array(texts, max_sentences_per_chunk=2)  # Puedes ajustar el número

# Inserta cada chunk en tu vectorstore
for chunk in chunks:
    # Aquí deberías agregar el chunk al vectorstore usando tu método habitual, por ejemplo:
    # vectorstore.add_texts([chunk])
    # agrega una impresion en consola de cada chunk
    print('Chunk: ' + chunk)




# dividir el texto en fragmentos
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(docs)

# embedding_function=HuggingFaceEmbeddings(model_name="nomic-embed-text", model_kwargs={'device': 'cuda:0'})
embedding_function = OllamaEmbeddings(model='nomic-embed-text')
print(len(docs))

vectorstore = Chroma(
    embedding_function=embedding_function, 
    collection_name=os.getenv('COLLECTION_VDB_NAME'),
    persist_directory=os.getenv('VECTOR_DB_PATH')
)

uuids = [str(uuid4()) for _ in range(len(docs))]
vectorstore.add_documents(documents=docs, ids=uuids)

print(vectorstore._collection.count())

def returnCollectionSize(): 
    print(vectorstore._collection.count())


