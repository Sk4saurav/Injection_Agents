import json
from huggingface_hub import InferenceClient
from config import HF_API_KEY, HF_MODEL_ID

print("[*] Using Hugging Face Chat Client...")

client = InferenceClient(
    model=HF_MODEL_ID,
    token=HF_API_KEY
)

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=512,
            temperature=0.0
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"HF Error: {e}"


def ask_llm_json(system_prompt: str, user_prompt: str) -> dict:
    raw = ask_llm(system_prompt, user_prompt)

    try:
        return json.loads(raw)
    except:
        return {"error": "json_parse_failed", "raw": raw[:500]}
