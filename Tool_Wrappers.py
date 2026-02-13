import subprocess
import json
import os
from config import SQLMAP_CMD, COMMIX_SCRIPT, NOSQLI_CMD, MAX_COMMIX_TIME, MAX_NOSQLI_TIME

def run_sqlmap(url, method="GET", data=None, cookies=None, dbms_hint=None):
    cmd = [SQLMAP_CMD, "-u", url, "--batch", "--random-agent"]

    if dbms_hint:
        cmd += ["--dbms", dbms_hint]

    if method == "POST" and data:
        flat = "&".join(f"{k}={v}" for k, v in data.items())
        cmd += ["--data", flat]

    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        cmd += ["--cookie", cookie_str]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"sqlmap error: {e}"


def run_commix(url, method="GET", data=None, cookies=None):
    if not os.path.exists(COMMIX_SCRIPT):
        return "commix not installed"

    cmd = ["python3", COMMIX_SCRIPT, "--url", url, "--batch", "--random-agent"]

    if method == "POST" and data:
        cmd += ["--data", json.dumps(data)]

    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        cmd += ["--cookie", cookie_str]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_COMMIX_TIME)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"commix error: {e}"


def run_nosqli(url, data=None):
    cmd = [NOSQLI_CMD, "scan", "-t", url]

    if data:
        cmd += ["-d", json.dumps(data)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_NOSQLI_TIME)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"nosqli error: {e}"
