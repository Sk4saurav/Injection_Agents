# detectors.py
import json
import llm_helper
import Tool_Wrappers
import utils
from config import SAFE_MODE


# ========================
# Agent 10 & 11: SQLi Detector (Enhanced)
# ========================

def detect_sqli(target: dict) -> dict:
    """
    Handles SQLi targets (both GET and POST) using sqlmap.
    Enhanced with Cookie/CSRF support.
    """
    print(f"\n[SQLi Agent] Testing: {target['name']}")

    url = target["url"]
    method = target.get("method", "GET")
    data = target.get("data")
    params = target.get("params", {})
    cookies = target.get("cookies")
    csrf = target.get("csrf_token")
    dbms = target.get("dbms_hint")

    # Step 1: Run sqlmap with new args
    raw_output = Tool_Wrappers.run_sqlmap(
        url=url,
        method=method,
        data=data,
        cookies=cookies,
        csrf_token=csrf,
        dbms_hint=dbms
    )

    # Step 2: Save Evidence
    utils.save_evidence(target["name"], "sqlmap", raw_output, "evidence")
    
    # Step 3: Sanitize & Analyze
    clean_output = utils.sanitize_output(raw_output)
    
    system_prompt = (
        "You are an expert web penetration tester specializing in SQL injection. "
        "Your job is to interpret sqlmap output and decide if there is a real vulnerability."
    )

    user_prompt = f"""We tested the following target for SQL injection:

Name: {target['name']}
URL: {url}
Method: {method}
Parameters: {params or data}
Auth Hint: Cookies/CSRF present.

Here is sqlmap output (sanitized):
{clean_output[:3000]}

Please answer in JSON with this schema:
{{
  "vulnerable": "yes/no/unknown",
  "technique": "error-based|union-based|boolean-blind|time-blind|stacked|none",
  "dbms_hint": "e.g. MySQL, PostgreSQL, or null if unknown",
  "parameter": "parameter name that is vulnerable",
  "impact_summary": "short description",
  "exploit_suggested": "yes/no",
  "exploit_hint": "optional: how to exploit further"
}}
"""

    llm_json = llm_helper.ask_llm_json(system_prompt, user_prompt)

    result = {
        "agent": "SQLi_Agent",
        "target_name": target["name"],
        "url": url,
        "method": method,
        "params_or_data": params or data,
        "sqlmap_output_snippet": clean_output[:600],
        "llm_analysis": llm_json,
    }
    return result


# ========================
# Agent 13 & 14: CmdInj Detector (Merged & Enhanced)
# ========================

def detect_cmdinj(target: dict, evidence_dir: str) -> dict:
    """
    Handles OS command injection (Linux/Windows/PowerShell) using commix.
    FIX: Merged Linux/Windows logic. Added PowerShell payloads.
    """
    print(f"\n[CmdInj Agent] Testing: {target['name']}")

    url = target["url"]
    method = target.get("method", "GET")
    data = target.get("data")
    params = target.get("params", {})
    os_hint = target.get("os_hint", "Linux") # Default to Linux if not set
    headers = target.get("headers")
    cookies = target.get("cookies")

    # Step 1: Run commix
    raw_output = Tool_Wrappers.run_commix(
        url=url,
        method=method,
        data=data,
        headers=headers,
        cookies=cookies,
        os_hint=os_hint
    )

    # Step 2: Save Evidence
    utils.save_evidence(target["name"], "commix", raw_output, evidence_dir)
    
    # Step 3: Sanitize & Analyze
    clean_output = utils.sanitize_output(raw_output)

    system_prompt = (
        "You are an expert web penetration tester specializing in OS command injection. "
        "Your job is to interpret commix output and HTTP responses."
    )

    user_prompt = f"""We tested the following target for command injection:

Name: {target['name']}
URL: {url}
Method: {method}
OS Hint: {os_hint} (Note: commix often auto-detects OS)
Parameters: {params or data}

Here is commix output (sanitized):
{clean_output[:3000]}

Please answer in JSON:
{{
  "vulnerable": "yes/no/unknown",
  "injection_type": "direct-output|blind|none",
  "evidence_summary": "what in output indicates command injection",
  "exploit_suggested": "yes/no",
  "exploit_hint": "optional next step"
}}
"""

    llm_json = llm_helper.ask_llm_json(system_prompt, user_prompt)

    result = {
        "agent": f"CmdInj_Agent", # Unified agent name
        "target_name": target["name"],
        "url": url,
        "method": method,
        "params_or_data": params or data,
        "commix_output_snippet": clean_output[:600],
        "llm_analysis": llm_json,
    }
    return result


# ========================
# Agent 12: NoSQLi (Mongo) Detector (Fixed JSON)
# ========================

def detect_nosqli(target: dict, evidence_dir: str) -> dict:
    """
    Handles NoSQL injection (MongoDB-style) using nosqli tool.
    FIX: Uses json.dumps for valid JSON payloads.
    """
    print(f"\n[NoSQLi Agent] Testing: {target['name']}")

    url = target["url"]
    method = target.get("method", "POST")
    data = target.get("data")
    params = target.get("params", {})
    os_hint = target.get("os_hint", "Linux")
    headers = target.get("headers", {"Content-Type": "application/json"})
    cookies = target.get("cookies")

    # Step 1: Run nosqli tool
    # FIX: Pass data as JSON string, not flattened
    raw_output = Tool_Wrappers.run_nosqli(
        url=url,
        data=data if method == "POST" else None,
        os_hint=os_hint
    )

    # Step 2: Save Evidence
    utils.save_evidence(target["name"], "nosqli", raw_output, evidence_dir)
    
    # Step 3: Sanitize & Analyze
    clean_output = utils.sanitize_output(raw_output)

    system_prompt = (
        "You are an expert web penetration tester specializing in NoSQL injection, especially MongoDB. "
        "Your job is to analyze output from nosqli tool and decide if there is a real vulnerability."
    )

    user_prompt = f"""We tested the following target for NoSQL injection using nosqli tool:

Name: {target['name']}
URL: {url}
Method: {method}
Parameters: {params or data}

Here is nosqli output (sanitized):
{clean_output[:3000]}

Please answer in JSON:
{{
  "vulnerable": "yes/no/unknown",
  "injection_type": "error-based|boolean-blind|timing|none",
  "payload_hint": "short hint about what kind of payload succeeded",
  "evidence_summary": "what in output suggests NoSQLi",
  "exploit_suggested": "yes/no",
  "exploit_hint": "optional next step"
}}
"""

    llm_json = llm_helper.ask_llm_json(system_prompt, user_prompt)

    result = {
        "agent": "NoSQLi_Agent_nosqli",
        "target_name": target["name"],
        "url": url,
        "method": method,
        "params_or_data": params or data,
        "nosqli_output_snippet": clean_output[:600],
        "llm_analysis": llm_json,
    }
    return result