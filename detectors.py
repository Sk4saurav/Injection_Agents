import llm_helper
import tool_wrappers
import utils

def detect_sqli(target: dict) -> dict:
    print(f"[SQLi] Testing {target['name']}")

    raw = tool_wrappers.run_sqlmap(
        url=target.get("url"),
        method=target.get("method", "GET"),
        data=target.get("data"),
        cookies=target.get("cookies"),
        dbms_hint=target.get("dbms_hint")
    )

    utils.save_evidence(target["name"], "sqlmap", raw)

    prompt = (
        "Analyze SQLMap output and return JSON:\n"
        '{"vulnerable":"yes/no","impact":"..."}\n\n'
        + raw[:2000]
    )

    analysis = llm_helper.ask_llm_json("You are a pentester.", prompt)
    return {"target": target["name"], "type": "SQLi", "analysis": analysis}


def detect_cmdinj(target: dict, evidence_dir="evidence") -> dict:
    print(f"[CmdInj] Testing {target['name']}")

    raw = tool_wrappers.run_commix(
        url=target.get("url"),
        method=target.get("method", "GET"),
        data=target.get("data"),
        cookies=target.get("cookies")
    )

    utils.save_evidence(target["name"], "commix", raw)

    prompt = (
        "Analyze command injection scan output and return JSON:\n"
        '{"vulnerable":"yes/no","evidence":"..."}\n\n'
        + raw[:2000]
    )

    analysis = llm_helper.ask_llm_json("You are a security tester.", prompt)
    return {"target": target["name"], "type": "CmdInj", "analysis": analysis}


def detect_nosqli(target: dict, evidence_dir="evidence") -> dict:
    print(f"[NoSQLi] Testing {target['name']}")

    raw = tool_wrappers.run_nosqli(
        url=target.get("url"),
        data=target.get("data")
    )

    utils.save_evidence(target["name"], "nosqli", raw)

    prompt = (
        "Analyze NoSQL injection output and return JSON:\n"
        '{"vulnerable":"yes/no","details":"..."}\n\n'
        + raw[:2000]
    )

    analysis = llm_helper.ask_llm_json("You are a security tester.", prompt)
    return {"target": target["name"], "type": "NoSQLi", "analysis": analysis}
