from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
# from langchain_community.document_loaders import TextLoader
from uuid import uuid4

# loaders = [PyPDFLoader('./pdfs/brain-gliomas-patient.pdf')]
# loaders = [JSONLoader('./files/menu.json', jq_schema='.')] #cargamos el archivo a procesar
loaders = [DirectoryLoader('../menus/', glob='**/*.txt')]
# leer .txt
# loaders = [TextLoader('./files/info.txt', ))]

docs = []
for file in loaders:
    docs.extend(file.load())

# dividir el texto en fragmentos
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(docs)

# embedding_function=HuggingFaceEmbeddings(model_name="nomic-embed-text", model_kwargs={'device': 'cuda:0'})
embedding_function = OllamaEmbeddings(model='nomic-embed-text')
print(len(docs))

vectorstore = Chroma(
    embedding_function=embedding_function, 
    collection_name='menu_pc_test',
    persist_directory="../vectors/menu_pc_test"
)

uuids = [str(uuid4()) for _ in range(len(docs))]
vectorstore.add_documents(documents=docs, ids=uuids)

print(vectorstore._collection.count())

def returnCollectionSize(): 
    print(vectorstore._collection.count())


