from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def create_vectorstore(documents, openai_api_key):
    """Embed documents with per-doc fallback so one bad chunk does not abort the run."""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    skipped = []
    vectorstore = None

    for idx, doc in enumerate(documents):
        label = doc.metadata.get("source") if hasattr(doc, "metadata") else None
        label = label or f"document #{idx + 1}"
        try:
            tmp_store = FAISS.from_documents([doc], embeddings)
            if vectorstore is None:
                vectorstore = tmp_store
            else:
                vectorstore.merge_from(tmp_store)
        except Exception as exc:  # keep going on single-doc failures
            skipped.append(f"{label}: {exc}")

    if vectorstore is None:
        return None, skipped

    return vectorstore.as_retriever(), skipped
