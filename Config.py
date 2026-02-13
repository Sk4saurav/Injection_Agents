import os
import sys
from dotenv import load_dotenv

load_dotenv()

# ===== LLM =====
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")

if not HF_API_KEY:
    raise ValueError("HF_API_KEY missing in .env")

# ===== TOOLS =====
SQLMAP_CMD = "/usr/bin/sqlmap"
COMMIX_SCRIPT = "/usr/share/commix/commix.py"
NOSQLI_CMD = "/usr/bin/nosqli"

PYTHON_CMD = sys.executable

# ===== BEHAVIOR =====
SAFE_MODE = True
REQUEST_TIMEOUT = 30
MAX_COMMIX_TIME = 120
MAX_NOSQLI_TIME = 120
