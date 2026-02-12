# llm_helper.py (Alternative Version)
import os
from openai import OpenAI
from config import HF_API_KEY, HF_MODEL_ID, HF_INFERENCE_URL

# Use HF Token with OpenAI Client
# Note: You must use a model ID that supports the OpenAI chat format
client = OpenAI(
    base_url=HF_INFERENCE_URL, # Point to HF
    api_key=HF_API_KEY            # Use HF Token
)

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    resp = client.chat.completions.create(
        model=HF_MODEL_ID, # Use HF Model ID
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    return resp.choices[0].message.content

def ask_llm_json(system_prompt: str, user_prompt: str) -> dict:
    raw = ask_llm(system_prompt, user_prompt)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Simple regex extraction for JSON blocks
        import re
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return {"error": "Parse error", "raw": raw[:500]}