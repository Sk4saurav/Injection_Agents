# main.py
import json
import datetime
import os
from typing import List, Dict, Any

import config
import llm_helper
import Detectors
import utils


def print_legal_warning():
    """Prints mandatory legal compliance warning."""
    print("=" * 60)
    print("⚠️  LEGAL & ETHICAL WARNING ⚠️")
    print("Scanning systems without explicit authorization is illegal.")
    print("You must have permission (written/contract) for every target in config.py.")
    print("Unauthorized scanning violates laws (e.g., CFAA, Computer Misuse Act).")
    print("=" * 60)
    print()


def run_master_agent():
    """
    Main coordinator with security checks enabled.
    """
    # 1. Legal Warning
    print_legal_warning()

    # 2. Setup Evidence Directory
    evidence_dir = "evidence"
    if not os.path.exists(evidence_dir):
        try:
            os.makedirs(evidence_dir)
        except OSError as e:
            print(f"[!] Fatal: Could not create evidence directory: {e}")
            return

    # 3. Load and Validate Targets
    print(f"=== AI Injection Vulnerability Agent (Safe & Legal Mode) ===")
    print(f"[*] Loading targets from config...")
    
    targets_to_run = []
    for target in config.TARGETS:
        # Mandatory Authorization Check
        if not target.get("authorized", False):
            print(f"[!] BLOCKED: Target '{target['name']}' is NOT marked as authorized.")
            print(f"    Edit config.py and set 'authorized': True for this target ONLY if you have permission.")
            continue # Skip this target
        
        targets_to_run.append(target)

    if not targets_to_run:
        print("\n[!] No authorized targets found. Exiting.")
        return

    print(f"[+] Authorized targets loaded: {len(targets_to_run)}")

    all_results = []

    # 4. Run Scans
    for target in targets_to_run:
        ttype = target.get("type")

        print(f"\n[*] Starting scan for: {target['name']}")

        # Pass evidence_dir to detectors
        if ttype == "SQLi":
            result = Detectors.detect_sqli(target)
            all_results.append(result)
        elif ttype == "CmdInj":
            # FIX: Use the merged detect_cmdinj function
            result = Detectors.detect_cmdinj(target, evidence_dir)
            all_results.append(result)
        elif ttype == "NoSQLi":
            result = Detectors.detect_nosqli(target, evidence_dir)
            all_results.append(result)
        else:
            print(f"[!] Unsupported target type: {ttype}")

    # 5. Generate Reports
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Save Raw Results (JSON)
    raw_filename = f"scan_raw_{timestamp}.json"
    with open(raw_filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Raw results saved to {raw_filename}")

    # Ask LLM for summary
    print("\n[*] Generating executive summary with LLM...")
    summary = generate_summary_report(all_results)

    summary_filename = f"scan_summary_{timestamp}.json"
    with open(summary_filename, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[+] Executive summary saved to {summary_filename}")

    # Text Summary
    text_summary_filename = f"scan_summary_{timestamp}.txt"
    with open(text_summary_filename, "w", encoding="utf-8") as f:
        f.write(summary.get("summary_text", ""))
        f.write("\n\nPrioritized Findings:\n")
        for pf in summary.get("prioritized_findings", []):
            f.write(f"- [{pf['vuln_type']}] {pf['target_name']}\n")
            f.write(f"  Impact: {pf['impact']}\n")
            f.write(f"  Recommendation: {pf['recommendation']}\n\n")

    print(f"[+] Human-readable summary saved to {text_summary_filename}")
    print("\n=== Scan complete. Please review evidence/ folder for raw logs. ===")


def generate_summary_report(all_results: List[Dict[str, Any]]) -> str:
    """
    Ask LLM to produce a high-level summary and prioritized list of findings.
    """
    system_prompt = (
        "You are a senior security consultant writing an executive summary for a penetration test. "
        "Be concise, professional, and prioritize findings by severity."
    )

    user_prompt = f"""Here is the consolidated output from an automated injection vulnerability scanner.

{json.dumps(all_results, indent=2)}

Please:
1) Summarize overall security posture (critical/high/medium/low).
2) List each confirmed vulnerability with:
   - Target name
   - Vulnerability type (SQLi / CmdInj / NoSQLi)
   - Impact
3) Suggest order of remediation.
4) Keep your answer practical and suitable for developers and system owners.

Return a JSON like:
{{
  "overall_risk": "critical/high/medium/low/info",
  "summary_text": "3-5 sentences",
  "prioritized_findings": [
    {{
      "target_name": "...",
      "vuln_type": "SQLi/CmdInj/NoSQLi",
      "impact": "...",
      "recommendation": "..."
    }}
  ]
}}
"""

    return llm_helper.ask_llm_json(system_prompt, user_prompt)


if __name__ == "__main__":
    run_master_agent()