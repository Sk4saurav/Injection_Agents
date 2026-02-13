import subprocess
import json
import shutil
from config import SQLMAP_CMD, COMMIX_CMD, NOSQLI_CMD, MAX_COMMIX_TIME, MAX_NOSQLI_TIME


def tool_exists(tool):
    return shutil.which(tool) is not None


# ================= SQLMAP =================
def run_sqlmap(url, method="GET", data=None, cookies=None, dbms_hint=None):

    if not tool_exists(SQLMAP_CMD):
        return "sqlmap not installed on system"

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


# ================= COMMIX =================
def run_commix(url, method="GET", data=None, cookies=None):

    if not tool_exists(COMMIX_CMD):
        return "commix not installed on system"

    cmd = [COMMIX_CMD, "--url", url, "--batch", "--random-agent"]

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


# ================= NOSQL =================
def run_nosqli(url, data=None):

    if not tool_exists(NOSQLI_CMD):
        return "nosqlmap not installed on system"

    cmd = [NOSQLI_CMD, "--help"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_NOSQLI_TIME)
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"nosqli error: {e}"
