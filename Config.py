# config.py
import os

# --- Hugging Face Settings (Replacing OpenAI) ---
HF_API_KEY = os.getenv("HF_API_KEY") # <--- Paste your token here
# You can also specify a specific model if you want
HF_MODEL_ID = "mistralai/Mistral-7b-Instruct-v0.2" # Example: Fast, smart, good for reasoning
# HF_INFERENCE_URL = "https://api-inference.huggingface.co" # Default HF endpoint

# --- Tool Paths (Unchanged) ---
SQLMAP_CMD = "sqlmap"
COMMIX_SCRIPT = "commix/commix.py"
NOSQLI_CMD = "nosqli"

# --- Scan Behavior (Unchanged) ---
SAFE_MODE = True
MAX_THREADS = 2
REQUEST_TIMEOUT = 30
MAX_COMMIX_TIME = 120
MAX_NOSQLI_TIME = 120

# --- Targets (Unchanged) ---
TARGETS = [
    {
        "name": "SQLi-GET-01-LocalLab",
        "type": "SQLi",
        "method": "GET",
        "url": "http://localhost:8080/listproducts.php?cat=1",
        "params": {"cat": "1"},
        "authorized": True,
        "cookies": {"PHPSESSID": "test_session_id"},
        "csrf_token": None,
        "dbms_hint": "MySQL"
    },
    # ... your other targets
]