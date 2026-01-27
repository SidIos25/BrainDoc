import os
import pickle

HISTORY_PATH = "chat_history.pkl"
MAX_HISTORY_ITEMS = 200

def load_chat_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "rb") as f:
            return pickle.load(f)
    return []

def save_chat_history(history):
    trimmed_history = history[-MAX_HISTORY_ITEMS:]
    with open(HISTORY_PATH, "wb") as f:
        pickle.dump(trimmed_history, f)
