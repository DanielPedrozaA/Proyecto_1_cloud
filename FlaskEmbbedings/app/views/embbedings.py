import re
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import  START, StateGraph
from typing_extensions import List,  TypedDict
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain import hub
import os


class State(TypedDict):
    question: str
    context: List[Document]
    answer: str
    collection: str

# Crear nuevo usuario
def embbedings():

    loader = TextLoader(r"C:\Users\mateo\Documents\Cloud\Proyecto_1_cloud\FlaskEmbbedings\test.txt",encoding= "utf-8")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(
        model="llama3",
    )

    collection_name = "CNN"
    chroma_path = "./chroma_db" 

    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=chroma_path, collection_name=collection_name)

    print(f"📂 Se han guardado {len(docs)} fragmentos en ChromaDB.")

    return {'mensaje': "Se ha guardado con exito"}, 200


def retrieve(state: State):

    chroma_path = "./chroma_db"  # Directorio donde se guardaron los embeddings
    collection_name = state["collection"]  # Asegúrate de usar el mismo nombre de colección

    embeddings = OllamaEmbeddings(
        model="llama3",
    )

    vector_store = Chroma(
        persist_directory=chroma_path,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    retrieved_docs = vector_store.similarity_search(state["question"])

    return {"context": retrieved_docs}


def generate(state: State):
    llm = init_chat_model("llama3", model_provider="ollama")
    prompt = hub.pull("rlm/rag-prompt")

    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


def question(data):

    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    response = graph.invoke({"question": data["question"], "collection": data["collection"]})

    return {"respuesta": response["answer"]}