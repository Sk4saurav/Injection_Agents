import json
import re
from huggingface_hub import InferenceClient
from config import HF_API_KEY, HF_MODEL_ID

print("[*] Using Hugging Face Chat Client...")

# Create HF client
client = InferenceClient(
    model=HF_MODEL_ID,
    token=HF_API_KEY,
)

# =========================
# Send prompt to LLM
# =========================
def ask_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Sends prompt to HuggingFace chat model
    Returns raw text response
    """

    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=1200,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"HF Error: {e}"


# =========================
# Extract JSON from LLM
# =========================
def ask_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Calls LLM and safely extracts JSON even if surrounded by text/markdown
    """

    raw = ask_llm(system_prompt, user_prompt)

    # ---- Try markdown ```json blocks ----
    match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # ---- Try any {...} block ----
    match = re.search(r"(\{.*\})", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # ---- Fallback error ----
    return {
        "error": "json_parse_failed",
        "raw": raw[:800]
    }
