# app.py (Streamlit UI entry point)

import streamlit as st
import os
from dotenv import load_dotenv
from modules.file_loader import load_documents
from modules.embedder import create_vectorstore
from modules.qa_chain import build_qa_chain
from modules.memory_manager import load_chat_history, save_chat_history


SUSPECT_PATTERNS = [
    "ignore previous instructions",
    "forget previous",
    "system prompt",
    "override safety",
    "social security",
    "ssn",
    "password",
]


def is_question_safe(question: str):
    lowered = question.lower()

    if len(question) > 2000:
        return False, "Question too long; please shorten."

    if any(pattern in lowered for pattern in SUSPECT_PATTERNS):
        return False, "Detected potentially unsafe or PII-seeking instruction."

    return True, ""

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="BrainDoc AI - Document Intelligence", layout="wide")

# Minimal, Apple/ChatGPT-inspired styling
st.markdown(
    """
    <style>
    /* Base layout */
    .stApp {background: linear-gradient(135deg, #f9fafb 0%, #f0f4ff 100%); color: #1a1d23 !important;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px;}

    /* Cards and pills */
    .glass-card {background: #ffffff; border: 1px solid #e0e7ff; border-radius: 16px; padding: 1.25rem; box-shadow: 0 12px 30px rgba(79,70,229,0.08);} 
    .subtle {color: #4a4f57; font-size: 0.9rem;}
    .pill {display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 999px; background: #e0e7ff; color: #4f46e5; font-size: 0.85rem; font-weight: 600;}
    
    /* Ensure all text is visible */
    p, span, div, label, h1, h2, h3, input, textarea {color: #1a1d23 !important;}

    /* Inputs and form elements */
    textarea, input, .stTextInput > div > div > input {background: #ffffff !important; color: #1a1d23 !important; border: 2px solid #e0e7ff !important; border-radius: 12px; padding: 0.65rem 0.85rem; transition: border-color 0.2s;}
    textarea:focus, input:focus, .stTextInput > div > div > input:focus {border-color: #4f46e5 !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.1) !important;}
    
    /* Select boxes - force visibility */
    .stSelectbox {border-radius: 10px;}
    .stSelectbox > div > div {background: #ffffff !important; border: 2px solid #e0e7ff !important; border-radius: 12px;}
    .stSelectbox > div > div > div {background: #ffffff !important; color: #1a1d23 !important;}
    .stSelectbox [data-baseweb="select"] {background: #ffffff !important;}
    .stSelectbox [data-baseweb="select"] > div {background: #ffffff !important; color: #1a1d23 !important; font-weight: 500;}
    .stSelectbox [role="button"] {background: #ffffff !important;}
    .stSelectbox [role="button"] > div {color: #1a1d23 !important;}
    .stSelectbox option, .stSelectbox li {background: #ffffff !important; color: #1a1d23 !important;}
    
    /* Dropdown menu items */
    [data-baseweb="popover"] {background: #ffffff !important;}
    [data-baseweb="popover"] ul {background: #ffffff !important;}
    [data-baseweb="popover"] li {background: #ffffff !important; color: #1a1d23 !important; padding: 0.6rem 1rem !important;}
    [data-baseweb="popover"] li:hover {background: #f0f4ff !important; color: #4f46e5 !important;}
    [data-baseweb="popover"] div {background: #ffffff !important; color: #1a1d23 !important;}
    [role="listbox"] {background: #ffffff !important;}
    [role="option"] {background: #ffffff !important; color: #1a1d23 !important;}
    [role="option"]:hover {background: #f0f4ff !important; color: #4f46e5 !important;}
    [data-baseweb="menu"] {background: #ffffff !important;}
    [data-baseweb="menu"] li {background: #ffffff !important; color: #1a1d23 !important;}
    [data-baseweb="list-item"] {background: #ffffff !important; color: #1a1d23 !important;}
    [data-baseweb="list-item"]:hover {background: #f0f4ff !important; color: #4f46e5 !important;}
    ul[role="listbox"] {background: #ffffff !important;}
    ul[role="listbox"] li {background: #ffffff !important; color: #1a1d23 !important;}
    
    select {background: #ffffff !important; color: #1a1d23 !important;}
    
    /* File uploader */
    [data-testid="stFileUploader"] {background: #ffffff !important; border: 2px dashed #e0e7ff; border-radius: 14px; padding: 1.5rem; text-align: center;}
    [data-testid="stFileUploader"] section {background: #ffffff !important; text-align: center;}
    [data-testid="stFileUploader"] label {color: #1a1d23 !important; text-align: center !important; display: block !important; font-size: 1.15rem !important; font-weight: 600 !important; margin-bottom: 1rem !important;}
    [data-testid="stFileUploader"] span, [data-testid="stFileUploader"] p {color: #1a1d23 !important; text-align: center !important;}
    [data-testid="stFileUploader"] small {text-align: center !important; display: block !important;}
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1.8rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0 auto !important;
        display: block !important;
        margin: 0 auto !important;
        display: inline-block !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(79,70,229,0.3) !important;
    }
    
    /* All labels */
    label {color: #1a1d23 !important; font-weight: 500;}
    
    /* Hide help/tooltip icons - cleaner look */
    [data-testid="stTooltipIcon"] {display: none !important;}
    button[kind="icon"] {display: none !important;}
    [aria-label*="help"] {display: none !important;}
    [data-baseweb="button"][kind="icon"] {display: none !important;}
    
    /* Title and caption styling */
    h1 {font-size: 2.8rem !important; font-weight: 800 !important; letter-spacing: -0.02em !important; background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;}
    .stCaption {font-size: 1.05rem !important; color: #6b7280 !important; font-weight: 400 !important; margin-top: 0.5rem !important;}
    
    /* File uploader label styling */
    [data-testid="stFileUploader"] > label > div:first-child {font-size: 1.15rem !important; font-weight: 600 !important; text-align: center !important; color: #1a1d23 !important; margin-bottom: 1rem !important;}
    
    /* Tooltips and help text - comprehensive fix */
    [role="tooltip"] {background: #1a1d23 !important; color: #ffffff !important; padding: 0.5rem 0.75rem !important; border-radius: 8px !important; font-size: 0.85rem !important;}
    [role="tooltip"] * {color: #ffffff !important;}
    .stTooltipContent {background: #1a1d23 !important; color: #ffffff !important;}
    [data-baseweb="tooltip"] {background: #1a1d23 !important; color: #ffffff !important;}
    [data-baseweb="tooltip"] * {color: #ffffff !important;}
    div[role="tooltip"] > div {background: #1a1d23 !important; color: #ffffff !important;}
    [class*="tooltip"] {background: #1a1d23 !important; color: #ffffff !important;}
    [class*="Tooltip"] {background: #1a1d23 !important; color: #ffffff !important;}
    [class*="Tooltip"] * {color: #ffffff !important;}
    
    /* Q&A bubbles */
    .qa-bubble {background: #ffffff; border: 1px solid #e0e7ff; border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 12px rgba(79,70,229,0.08);} 
    .qa-label {font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280 !important; margin-bottom: 0.4rem;}
    .qa-text {color: #1a1d23 !important; line-height: 1.6; font-size: 0.95rem;}

    /* Expanders - keep text readable on non-hover */
    div[data-testid="stExpander"] {background: #ffffff !important; border: 1px solid #e0e7ff !important; border-radius: 12px !important;}
    div[data-testid="stExpander"] summary {background: #ffffff !important; color: #1a1d23 !important; font-weight: 600 !important;}
    div[data-testid="stExpander"] summary:hover {background: #f0f4ff !important; color: #4f46e5 !important;}
    div[data-testid="stExpander"] * {color: #1a1d23 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧠✨ BrainDoc AI")
st.markdown('<p style="text-align: center; font-size: 1.15rem; color: #4f46e5; margin-top: -1rem; margin-bottom: 2.5rem; font-weight: 600;">Unlock Insights from Every Document</p>', unsafe_allow_html=True)

# Load chat history into session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "last_question" not in st.session_state:
    st.session_state.last_question = None

# Layout: controls on the left, chat on the right
controls_col, chat_col = st.columns([1, 1.6], gap="large")

# Sidebar branding
st.sidebar.markdown(
        """
        <div style="padding: 0 0 1rem 0;">
            <div style="font-size: 1.3rem; font-weight: 800; color:#4f46e5;">🧠✨ BrainDoc AI</div>
            <div style="font-size:0.9rem;color:#6b7280;">Unlock Insights from Every Document</div>
        </div>
        """,
        unsafe_allow_html=True,
)

with controls_col:
    domain = st.selectbox("Document Domain", ["Healthcare", "Legal", "Finance", "Education"], help="Prompts adapt tone and focus per domain.")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Drop multiple files; they will be indexed together.",
    )

with chat_col:
    st.markdown("### Ask Questions")

    if not uploaded_files:
        st.info("Upload at least one document to start asking questions.")
    elif not openai_api_key:
        st.warning("Set OPENAI_API_KEY in your .env to generate answers.")
    else:
        with st.spinner("Processing documents..."):
            all_docs, load_errors = load_documents(uploaded_files)

        if load_errors:
            st.warning("Some files could not be processed:\n" + "\n".join(load_errors))

        if all_docs:
            retriever = create_vectorstore(all_docs, openai_api_key)
            qa_chain = build_qa_chain(retriever, openai_api_key, domain)

            st.sidebar.markdown("### Session Metrics")
            st.sidebar.metric("Documents Uploaded", len(uploaded_files))
            st.sidebar.metric("Chunks Indexed", len(all_docs))
            st.sidebar.metric("Total Questions Asked", len(st.session_state.chat_history))
            if load_errors:
                st.sidebar.write(f"File warnings: {len(load_errors)}")

            # Sidebar chat history (only after documents are processed)
            st.sidebar.markdown("### 💬 Chat History")
            if st.session_state.chat_history:
                for idx, (q, a) in enumerate(reversed(st.session_state.chat_history), 1):
                    st.sidebar.markdown(f"""
                        <div style="background: #ffffff; border: 1px solid #e5e6eb; border-radius: 10px; padding: 0.75rem; margin-bottom: 0.75rem;">
                           <div style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280; margin-bottom: 0.3rem;">Question {idx}</div>
                           <div style="color: #1a1d23; font-size: 0.85rem; line-height: 1.5;">{q}</div>
                         </div>
                    """, unsafe_allow_html=True)
                    answer_preview = a[:120] + "..." if len(a) > 120 else a
                    st.sidebar.markdown(f"""
                        <div style="background: #f7f8fa; border: 1px solid #e5e6eb; border-radius: 10px; padding: 0.75rem; margin-bottom: 1rem;">
                           <div style="font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280; margin-bottom: 0.3rem;">Answer {idx}</div>
                           <div style="color: #1a1d23; font-size: 0.85rem; line-height: 1.5;">{answer_preview}</div>
                         </div>
                    """, unsafe_allow_html=True)
            else:
                st.sidebar.info("No chat history yet. Start a conversation!")

            # Chat input always visible when docs are ready
            user_question = st.text_input(
                "Type your question",
                placeholder="Ask about your documents...",
                label_visibility="collapsed",
            )

            if user_question:
                is_safe, reason = is_question_safe(user_question)
                if not is_safe:
                    st.warning(f"Question blocked for safety: {reason}")
                else:
                    with st.spinner("Generating answer..."):
                        try:
                            result = qa_chain.run(user_question)
                            answer = result["answer"] if isinstance(result, dict) and "answer" in result else result
                            sources = result["sources"] if isinstance(result, dict) and "sources" in result else []
                            st.session_state.chat_history.append((user_question, answer))
                            save_chat_history(st.session_state.chat_history)
                            st.session_state.last_question = user_question
                            st.session_state.last_answer = answer
                            st.session_state.last_sources = sources
                        except Exception as exc:
                            st.error(f"Could not generate an answer: {exc}")
            # Show the most recent answer prominently before history
            if st.session_state.last_answer:
                st.markdown("---")
                st.markdown("#### Latest Answer")
                st.markdown(
                    f'<div class="qa-bubble"><div class="qa-label">Question</div><div class="qa-text">{st.session_state.last_question}</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="qa-bubble" style="background:#f7f8fa;"><div class="qa-label">Answer</div><div class="qa-text">{st.session_state.last_answer}</div></div>',
                    unsafe_allow_html=True,
                )
                if "last_sources" in st.session_state and st.session_state.last_sources:
                    st.markdown("**📄 Sources Used:**")
                    for i, doc in enumerate(st.session_state.last_sources, 1):
                        preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                        st.caption(f"**Chunk {i}:** {preview}")
            # Show previous conversations as expandable dropdowns with full text
            if st.session_state.chat_history:
                st.markdown("---")
                st.markdown("#### Previous Conversations")
                history = list(reversed(st.session_state.chat_history))
                for idx, (q, a) in enumerate(history, 1):
                    label_q = q if len(q) <= 90 else q[:90] + "..."
                    with st.expander(f"Conversation {idx}: {label_q}", expanded=False):
                        st.markdown("**Question**")
                        st.write(q)
                        st.markdown("**Answer**")
                        st.write(a)
        else:
            st.error("No documents were processed successfully.")
