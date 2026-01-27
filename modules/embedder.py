from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def create_vectorstore(documents, openai_api_key):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(documents, embeddings)
    return vectorstore.as_retriever()
