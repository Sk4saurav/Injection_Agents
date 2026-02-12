# utils.py
import re
import os
import datetime

def sanitize_output(text: str) -> str:
    """
    Redacts sensitive information like passwords and API keys from logs/reports.
    """
    if not text:
        return ""
    
    patterns = [
        r"(password['\"]?\s*[:=]\s*)(['\"]?[^'\"]+)(['\"]?)", 
        r"(passwd['\"]?\s*[:=]\s*)(['\"]?[^'\"]+)(['\"]?)",
        r"(api_key['\"]?\s*[:=]\s*)(['\"]?[^'\"]+)(['\"]?)",
        r"(token['\"]?\s*[:=]\s*)(['\"]?[^'\"]+)(['\"]?)",
        r"(secret['\"]?\s*[:=]\s*)(['\"]?[^'\"]+)(['\"]?)"
    ]
    
    redacted_text = text
    for pattern in patterns:
        redacted_text = re.sub(pattern, r"\1[REDACTED]\3", redacted_text, flags=re.IGNORECASE)
        
    return redacted_text


def save_evidence(target_name: str, tool_name: str, raw_output: str, evidence_dir: str = "evidence"):
    """
    Saves raw tool output to an evidence folder for audit trails.
    """
    if not os.path.exists(evidence_dir):
        try:
            os.makedirs(evidence_dir)
            print(f"[+] Created evidence directory: {evidence_dir}")
        except OSError as e:
            print(f"[!] Could not create evidence directory: {e}")
            return

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = target_name.replace("/", "-").replace(":", "-")
    filename = f"{evidence_dir}/{tool_name}_{safe_name}_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(raw_output)
        print(f"[+] Evidence saved to {filename}")
    except IOError as e:
        print(f"[!] Could not save evidence: {e}")