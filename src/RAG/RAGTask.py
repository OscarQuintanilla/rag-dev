from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI
import json
from langchain.chains import RetrievalQA

# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

embedding_function=OllamaEmbeddings(model='nomic-embed-text')
vectorstore = Chroma(
    collection_name='menu_pc_test',
    persist_directory="../vectors/menu_pc_test", 
    embedding_function=embedding_function
    )
print(f"Número de documentos en la bdd: {vectorstore._collection.count()}")

history = [
    {"role": "system", "content": "Eres un chatbot que realiza las labores de cajero en el restaurante Pollo Campestre. Siempre devuelves respuestas a corde a ese empleo, manteniendo el respeto y caballerosidad pero a la vez te mantienes conciso y preciso."},
    {"role": "assistant", "content": "Eres un chatbot que realiza las labores de cajero en el restaurante Pollo Campestre. Siempre devuelves respuestas a corde a ese empleo, manteniendo el respeto y caballerosidad pero a la vez te mantienes conciso y preciso."},
]

while True:
    completion = client.chat.completions.create(
        model="local-model", # this field is currently unused
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content

    # history.append(new_message)
    
    # # Uncomment to see chat history
    # import json
    # gray_color = "\033[90m"
    # reset_color = "\033[0m"
    # print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
    # print(json.dumps(history, indent=2))
    # print(f"\n{'-'*55}\n{reset_color}")

    # print()

    next_input = input("> ")
    # search_results = vector_db.similarity_search(next_input, k=2)
    some_context = "the clock is 12pm"

    print(f"Searching with input: {next_input}")
    search_results = vectorstore.similarity_search("pupusas", k=4)
    print(f"Found {len(search_results)} results from documents.")

    for result in search_results:
        some_context += result.page_content + "\n\n"
    history.append({"role": "user", "content": some_context + next_input})