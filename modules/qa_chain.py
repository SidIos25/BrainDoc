from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from modules.domain_prompts import get_domain_prompt


class SimpleQAChain:
    def __init__(
        self,
        retriever,
        openai_api_key,
        domain,
        max_source_docs: int = 4,
        max_context_chars_per_doc: int = 1800,
    ):
        prompts = get_domain_prompt(domain)
        # Use a single system instruction for more consistent model behavior.
        system_prompt = f"{prompts['prefix']}\n\n{prompts['suffix']}"

        self.retriever = retriever
        self.max_source_docs = max(1, int(max_source_docs))
        self.max_context_chars_per_doc = max(200, int(max_context_chars_per_doc))
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
        ])
        # Lower temperature improves factual consistency for document QA.
        self.llm = ChatOpenAI(temperature=0.3, openai_api_key=openai_api_key)

    def _retrieve(self, question: str):
        if hasattr(self.retriever, "get_relevant_documents"):
            return self.retriever.get_relevant_documents(question)
        if hasattr(self.retriever, "invoke"):
            return self.retriever.invoke(question)
        return []

    def _build_context(self, docs) -> str:
        if not docs:
            return "No relevant context found."

        chunks = []
        for doc in docs:
            content = getattr(doc, "page_content", "") or ""
            chunks.append(content[: self.max_context_chars_per_doc])
        return "\n\n".join(chunks)

    def _select_sources(self, docs):
        return docs[: self.max_source_docs]

    def run(self, question: str) -> dict:
        docs = self._retrieve(question)
        if docs is None:
            docs = []
        elif hasattr(docs, "page_content"):
            docs = [docs]

        selected_docs = self._select_sources(docs)
        context = self._build_context(selected_docs)
        messages = self.prompt.format_messages(context=context, question=question)
        response = self.llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        return {"answer": answer, "sources": selected_docs}


def build_qa_chain(
    retriever,
    openai_api_key,
    domain,
    max_source_docs: int = 4,
    max_context_chars_per_doc: int = 1800,
):
    return SimpleQAChain(
        retriever,
        openai_api_key,
        domain,
        max_source_docs=max_source_docs,
        max_context_chars_per_doc=max_context_chars_per_doc,
    )
