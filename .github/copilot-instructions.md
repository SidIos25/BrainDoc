# Copilot Instructions (quick read)

- What this is: BrainDoc AI is a Streamlit RAG app for PDFs/DOCX/TXT with domain prompts (Healthcare, Legal, Finance, Education). Keep the polished UI styling and the safety checks.

- Core flow: upload files → file_loader saves temp copies and chunks text (800 size, 100 overlap) with PDF fallbacks (PyPDF → PDFPlumber → PyMuPDF) → embedder builds a FAISS retriever using OpenAI embeddings → qa_chain pulls up to 4 chunks, applies the domain prompt, and calls ChatOpenAI → chat history is persisted via memory_manager.

- Safety: `is_question_safe` blocks very long or suspect questions (e.g., "ignore previous instructions", "ssn", "password"). Loaders should return user-visible `load_errors` instead of raising.

- Prompts: domain text lives in domain_prompts; unknown domain falls back to Education. Update this map to add or tweak domains.

- UI rules: chat input only enabled after files and API key are present; latest answer is pinned, older turns sit in expanders; sidebar shows upload counts and history previews; a "Sources Used" section previews the top context chunks after each answer. CSS is embedded in app.py — adjust in place rather than replacing.

- Memory: chat turns are pickled to `chat_history.pkl`, capped at 200. Tests temporarily override `HISTORY_PATH`/`MAX_HISTORY_ITEMS`.

- Commands: `pip install -r requirements.txt`; set `OPENAI_API_KEY` in .env (dotenv loaded); `streamlit run app.py`; tests via `pytest -q`.

- Patterns: return `(docs, errors)` from loaders; keep chunk sizes consistent; `_retrieve` in `SimpleQAChain` must handle retrievers with `.get_relevant_documents` or `.invoke`.

- Extending: add domains by extending `DOMAIN_TEMPLATES` and matching the selectbox labels; change chunking or top-k by adjusting splitter settings or the `docs[:4]` slice in `SimpleQAChain`.

**Interview cheat sheet (30s answer)**
- "BrainDoc is a Streamlit RAG app: upload PDF/DOCX/TXT, we chunk (800/100), embed with OpenAI, index in FAISS, and ask ChatGPT with a domain-specific prompt."
- "Safety: we block long or PII-ish queries with `is_question_safe` and show loader errors instead of crashing."
- "UI: questions only after docs + API key; latest answer pinned; history in expanders; we also show 'Sources Used' with chunk previews."
- "Memory: chat turns pickled and trimmed to 200; tests cover loader fallbacks, domain defaulting, and history trimming."
