from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def create_vectorstore(documents, openai_api_key):
    """Create FAISS retriever with batched embedding and granular fallback on failures."""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    skipped = []
    vectorstore = None
    batch_size = 32

    def _label(doc, idx):
        label = doc.metadata.get("source") if hasattr(doc, "metadata") else None
        return label or f"document #{idx + 1}"

    for start in range(0, len(documents), batch_size):
        batch = documents[start : start + batch_size]
        try:
            tmp_store = FAISS.from_documents(batch, embeddings)
            if vectorstore is None:
                vectorstore = tmp_store
            else:
                vectorstore.merge_from(tmp_store)
            continue
        except Exception:
            # Fall back to per-doc embedding within a failed batch.
            pass

        for offset, doc in enumerate(batch):
            idx = start + offset
            label = _label(doc, idx)
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
