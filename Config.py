import os
from dotenv import load_dotenv

load_dotenv()

# ===== LLM =====
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY missing in .env")

# ===== TOOLS (portable names, not paths) =====
SQLMAP_CMD = "sqlmap"
COMMIX_CMD = "commix"
NOSQLI_CMD = "nosqlmap"

# ===== BEHAVIOR =====
SAFE_MODE = True
REQUEST_TIMEOUT = 30
MAX_COMMIX_TIME = 120
MAX_NOSQLI_TIME = 120
