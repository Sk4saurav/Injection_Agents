import os
import datetime

def save_evidence(name, tool, data, evidence_dir="evidence"):
    os.makedirs(evidence_dir, exist_ok=True)
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"{evidence_dir}/{tool}_{name}_{ts}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)

    print("[+] Evidence saved:", filename)
