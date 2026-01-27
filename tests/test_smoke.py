import os
from types import SimpleNamespace
import modules.memory_manager as memory_manager
from modules.domain_prompts import get_domain_prompt
from modules.file_loader import load_documents


def _upload(name: str, content: bytes):
    # Mimic Streamlit's UploadedFile minimal interface used by load_documents
    return SimpleNamespace(name=name, read=lambda: content)


def test_load_documents_txt_success(tmp_path):
    uploaded = _upload("note.txt", b"hello world")
    docs, errors = load_documents([uploaded])

    assert errors == []
    assert docs
    assert any("hello" in doc.page_content for doc in docs)


def test_load_documents_unsupported_type():
    uploaded = _upload("table.xlsx", b"data")
    docs, errors = load_documents([uploaded])

    assert docs == []
    assert errors and "Unsupported file type" in errors[0]


def test_domain_prompt_defaults_to_education():
    prompt = get_domain_prompt("UnknownDomain")

    assert prompt["prefix"].startswith("You are an education-focused assistant")
    assert "educational context" in prompt["suffix"].lower()


def test_memory_manager_trims_history(tmp_path):
    original_path = memory_manager.HISTORY_PATH
    original_max = memory_manager.MAX_HISTORY_ITEMS

    temp_path = tmp_path / "history.pkl"
    memory_manager.HISTORY_PATH = str(temp_path)
    memory_manager.MAX_HISTORY_ITEMS = 3

    try:
        history = [(f"q{i}", f"a{i}") for i in range(5)]
        memory_manager.save_chat_history(history)
        loaded = memory_manager.load_chat_history()

        assert len(loaded) == 3
        assert loaded[0][0] == "q2"
        assert loaded[-1][0] == "q4"
    finally:
        memory_manager.HISTORY_PATH = original_path
        memory_manager.MAX_HISTORY_ITEMS = original_max
        if os.path.exists(temp_path):
            os.remove(temp_path)
