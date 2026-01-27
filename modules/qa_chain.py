from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from modules.domain_prompts import get_domain_prompt


class SimpleQAChain:
    def __init__(self, retriever, openai_api_key, domain):
        prompts = get_domain_prompt(domain)
        system_prompt = prompts["prefix"]
        suffix_prompt = prompts["suffix"]

        self.retriever = retriever
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Context:\n{context}\n\nQuestion: {question}"),
            ("system", suffix_prompt),
        ])
        self.llm = ChatOpenAI(temperature=0.6, openai_api_key=openai_api_key)

    def _retrieve(self, question: str):
        if hasattr(self.retriever, "get_relevant_documents"):
            return self.retriever.get_relevant_documents(question)
        if hasattr(self.retriever, "invoke"):
            return self.retriever.invoke(question)
        return []

    def run(self, question: str) -> str:
        docs = self._retrieve(question)
        if docs is None:
            docs = []
        elif hasattr(docs, "page_content"):
            docs = [docs]

        context = "\n\n".join(doc.page_content for doc in docs[:4]) if docs else "No relevant context found."
        messages = self.prompt.format_messages(context=context, question=question)
        response = self.llm.invoke(messages)
        answer = response.content if hasattr(response, "content") else str(response)
        return {"answer": answer, "sources": docs[:4]}


def build_qa_chain(retriever, openai_api_key, domain):
    return SimpleQAChain(retriever, openai_api_key, domain)
