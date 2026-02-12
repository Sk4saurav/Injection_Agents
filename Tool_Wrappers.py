# tool_wrappers.py
import subprocess
import httpx
import json
from typing import Optional, Dict
import os

from Config import (
    SQLMAP_CMD, COMMIX_SCRIPT, NOSQLI_CMD,
    SAFE_MODE, MAX_COMMIX_TIME, MAX_NOSQLI_TIME, REQUEST_TIMEOUT
)

def check_tool_version(command: list, arg: str = "--version") -> bool:
    """Checks if a tool is installed."""
    try:
        subprocess.run([command[0], arg], check=True, capture_output=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_safe_args(tool_type: str) -> list:
    """Returns safe-mode arguments (e.g., rate limiting)."""
    if not SAFE_MODE:
        return []
    
    safe_args = []
    if tool_type == "sqlmap":
        # Force low risk and level to prevent data modification
        safe_args = ["--risk=1", "--level=1"]
    return safe_args

def run_sqlmap(url: str, method: str = "GET", data: Optional[Dict] = None, cookies: Optional[Dict] = None, dbms_hint: Optional[str] = None) -> str:
    """Executes sqlmap with safe args and auth support."""
    if not check_tool_version([SQLMAP_CMD]):
        return "Error: sqlmap not found."
    
    cmd = [SQLMAP_CMD, "-u", url, "--batch"]
    cmd.extend(get_safe_args("sqlmap"))

    if dbms_hint:
        cmd.extend([f"--dbms={dbms_hint}"])

    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        cmd.extend(["--cookie", cookie_str])

    if method == "POST" and data:
        # Flatten data for application/x-www-form-urlencoded
        flat = "&".join(f"{k}={v}" for k, v in data.items())
        cmd.extend(["--data", flat])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return "sqlmap timed out"
    except Exception as e:
        return f"sqlmap error: {e}"

def run_commix(url: str, method: str = "GET", data: Optional[Dict] = None, cookies: Optional[Dict] = None, os_hint: str = "Linux") -> str:
    """Executes commix with safe args and JSON support."""
    if not check_tool_version(["python", "--version"]): 
        return "Error: Python interpreter not found."
    if not os.path.exists(COMMIX_SCRIPT):
         return f"Error: Commix script not found at {COMMIX_SCRIPT}"

    cmd = ["python", COMMIX_SCRIPT, "--url", url, "--batch"]
    
    # Pass data as valid JSON string
    if method == "POST" and data:
        json_data_str = json.dumps(data)
        cmd.extend(["--data", json_data_str])
        
    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        cmd.extend(["--cookie", cookie_str])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_COMMIX_TIME)
        return result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return "commix timed out"
    except Exception as e:
        return f"commix error: {e}"

def run_nosqli(url: str, data: Optional[Dict] = None) -> str:
    """Executes nosqli with JSON support."""
    if not check_tool_version([NOSQLI_CMD]):
        return "Error: nosqli not found."

    cmd = ["nosqli", "scan", "-t", url]

    if data:
        # Use json.dumps to preserve NoSQL operators
        json_data_str = json.dumps(data)
        cmd.extend(["-d", json_data_str])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=MAX_NOSQLI_TIME)
        return result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        return "nosqli timed out"
    except Exception as e:
        return f"nosqli error: {e}"

def send_http_request(url: str, method: str = "GET", params: Optional[dict] = None, data: Optional[dict] = None, json_data: Optional[dict] = None, headers: Optional[dict] = None) -> httpx.Response:
    """Helper for manual HTTP checks if needed."""
    with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
        if method == "GET":
            return client.get(url, params=params, headers=headers)
        elif method == "POST":
            if json_data:
                return client.post(url, json=json_data, headers=headers)
            else:
                return client.post(url, data=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")