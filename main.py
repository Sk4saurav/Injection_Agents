import json
import datetime
import detectors


def ask_target():
    print("\n=== Target Input ===")

    name = input("Target name: ").strip()
    url = input("Target URL: ").strip()

    method = input("HTTP Method (GET/POST) [GET]: ").strip() or "GET"

    data = None
    if method.upper() == "POST":
        raw = input("POST data (key=value&key2=value2) or blank: ").strip()
        if raw:
            data = dict(item.split("=") for item in raw.split("&"))

    cookies = input("Cookies (key=value;key2=value2) or blank: ").strip()
    cookie_dict = None
    if cookies:
        cookie_dict = dict(item.split("=") for item in cookies.split(";"))

    return {
        "name": name,
        "method": method,
        "url": url,
        "data": data,
        "cookies": cookie_dict,
        "authorized": True
    }


def print_result(title, result):
    print("\n" + "="*60)
    print(f"[ RESULT ] {title}")
    print("="*60)

    if isinstance(result, dict):
        if "analysis" in result:
            analysis = result["analysis"]
            if isinstance(analysis, dict):
                for k, v in analysis.items():
                    print(f"{k.upper():15}: {v}")
            else:
                print(analysis)
        else:
            print(result)
    else:
        print(result)


def run_full_scan(target):
    print("\n=== AI Multi-Vector Injection Scanner ===")

    final_report = {}

    # SQLi
    try:
        print("\n[1/3] Testing SQL Injection...")
        sqli = detectors.detect_sqli(target)
        final_report["SQLi"] = sqli
        print_result("SQL Injection", sqli)
    except Exception as e:
        final_report["SQLi"] = {"error": str(e)}
        print("SQLi Error:", e)

    # CmdInj
    try:
        print("\n[2/3] Testing Command Injection...")
        cmd = detectors.detect_cmdinj(target)
        final_report["CmdInj"] = cmd
        print_result("Command Injection", cmd)
    except Exception as e:
        final_report["CmdInj"] = {"error": str(e)}
        print("CmdInj Error:", e)

    # NoSQLi
    try:
        print("\n[3/3] Testing NoSQL Injection...")
        nosql = detectors.detect_nosqli(target)
        final_report["NoSQLi"] = nosql
        print_result("NoSQL Injection", nosql)
    except Exception as e:
        final_report["NoSQLi"] = {"error": str(e)}
        print("NoSQLi Error:", e)

    # Save ONE combined report
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"scan_{target['name']}_{ts}.json"

    with open(filename, "w") as f:
        json.dump(final_report, f, indent=2)

    print("\n" + "="*60)
    print("SCAN COMPLETE")
    print("Report saved:", filename)
    print("="*60)


if __name__ == "__main__":
    run_full_scan(ask_target())
