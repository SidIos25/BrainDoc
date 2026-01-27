# BrainDoc AI — Document Intelligence

Tagline: Unlock Insights from Every Document.

BrainDoc AI is a Streamlit RAG app. Upload PDFs/DOCX/TXT, pick a domain (Healthcare, Legal, Finance, Education), and get contextual answers with source citations. Safety checks block risky queries; chat history is saved between turns.

---

## 🚀 Features

| Feature                          | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| 🔍 Domain Selection              | Choose Healthcare, Legal, Finance, or Education                             |
| 📄 Multi-file Upload             | Upload one or more PDFs, Word Docs, or TXT files                            |
| 💬 Contextual Q&A               | Ask specific questions about document content                               |
| 🧠 Custom Prompting             | Domain-aware prompts for tailored, relevant answers                         |
| 💾 Chat Memory + History        | Stores past interactions between sessions                                   |
| 📁 Sample Reports               | Try included examples in the `samples/` folder                             |
| 📎 Source Citations             | Shows the top context chunks used for each answer                           |
| 📊 Session Metrics              | Sidebar metrics: documents uploaded, chunks indexed, questions asked        |

---

## 🧭 How It Works
1) Upload & parse: User uploads PDF/DOCX/TXT; `file_loader` saves temp files, reads, and chunks text (800 size, 100 overlap) with PDF fallbacks (PyPDF → PDFPlumber → PyMuPDF).
2) Embed & index: `embedder` builds a FAISS vector store from chunks using OpenAI embeddings.
3) Domain-aware prompting: `domain_prompts` picks the prompt for Healthcare/Legal/Finance/Education.
4) Retrieval-augmented Q&A: `qa_chain` retrieves relevant chunks and queries the LLM with domain prompt + question.
5) Safety checks: `app.py` blocks very long or suspect questions before sending to the model.
6) Memory: `memory_manager` trims/saves chat history so answers stay concise across turns.
7) UI loop: Streamlit renders results, shows session metrics, and lets the user continue asking questions.
8) Sources: After answers, a “Sources Used” section previews the top context chunks.

High-level flow:

User → Upload files → Parse & chunk → Embed → FAISS search → Domain prompt + question → LLM answers → Store chat history

---

## 📁 Folder Structure

```
BrainDoc/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── chat_history.pkl
├── data/                       # 📄 Sample documents
│   ├── healthcare_sample.txt
│   ├── finance_example.txt
│   ├── legal_contract.txt
│   └── course_outline.txt
│
├── modules/
│   ├── file_loader.py
│   ├── embedder.py
│   ├── qa_chain.py
│   ├── memory_manager.py
│   └── domain_prompts.py
├── samples/                        # 📋 Domain-specific test documents
│   ├── COURSE_SYLLABUS.txt         (Education)
│   ├── SOFTWARE_LICENSE_AGREEMENT.txt  (Legal)
│   ├── MEDICAL_REPORT.txt          (Healthcare)
│   └── FINANCIAL_REPORT.txt        (Finance)
├── tests/
│   └── test_smoke.py
└── .github/
```

---

## 🧪 Quick Test with Sample Documents
Upload any file from the `samples/` folder to test each domain:

| Domain | Document | Try Asking |
|--------|----------|------------|
| 🏥 Healthcare | `MEDICAL_REPORT.txt` | "What are the critical health risks identified?" |
| ⚖️ Legal | `SOFTWARE_LICENSE_AGREEMENT.txt` | "What are the restrictions on the licensee?" |
| 💼 Finance | `FINANCIAL_REPORT.txt` | "What were the major revenue sources?" |
| 🎓 Education | `COURSE_SYLLABUS.txt` | "What are the course objectives?" |

---

## ⚙️ Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/braindoc.git
cd BrainDoc
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create your `.env` from the example**
```
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS/Linux
cp .env.example .env
```
Open `.env` and set your key:
```
OPENAI_API_KEY=your_openai_key_here
```

4. **Run the app**
```bash
streamlit run app.py
```

5. **(Optional) Lock exact versions for reproducibility**
```bash
pip freeze > requirements.lock
```

6. **Run tests locally**
```bash
pytest -q
```

---

## 📌 Roadmap Ideas
- Citations with sources
- Per-domain prompt fine-tuning
- PDF highlighting & annotations
- User login & cloud session storage
- Prompt safety: stronger PII/prompt-injection checks
- Evaluation: lightweight answer grading against expectations

---

## 🔒 Security
- Keep secrets out of Git: `.env` is ignored by `.gitignore` (use `.env.example` to share the shape).
- Before pushing, run `git status` to confirm `.env` and `chat_history.pkl` are not staged.

---

## 📜 License
MIT

---



