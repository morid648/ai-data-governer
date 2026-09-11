#!/usr/bin/env python3
"""
Workflow Sanitizer & Scaffolder (TASK-2.1 & TASK-9.1)
Prepares a sanitized, clean, production-ready n8n workflow JSON for AI Data Governor.
"""

import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(BASE_DIR, "data_governor_n8n_template.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "workflow", "ai_data_governor_workflow.json")
ALT_OUTPUT_PATH = os.path.join(BASE_DIR, "workflow", "data_governor_n8n_workflow.json")

def sanitize_workflow():
    print(f"Reading template from {TEMPLATE_PATH}...")
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        wf = json.load(f)

    # 1. Update workflow name
    wf["name"] = "AI Data Governor - Multi-Agent Audit & Remediation"
    
    # 2. Iterate nodes and sanitize
    nodes = wf.get("nodes", [])
    print(f"Sanitizing {len(nodes)} nodes...")
    
    for node in nodes:
        name = node.get("name", "")
        params = node.get("parameters", {})
        
        # Replace hardcoded test email addresses
        if "sendTo" in params:
            if "tony" in str(params["sendTo"]).lower() or "codebasics" in str(params["sendTo"]).lower():
                params["sendTo"] = "approver@example.com"
        
        # In email subjects and messages, standardize references to AI Data Governor
        for key in ["subject", "message"]:
            if key in params and isinstance(params[key], str):
                params[key] = params[key].replace("AtliQ Data Governor", "AI Data Governor")
                # Also replace greeting if it had a hardcoded person's name
                params[key] = re.sub(r"^[=]?Tony,", "=Team,", params[key])

    # 3. Ensure target directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # 4. Save sanitized workflow
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    with open(ALT_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated sanitized workflow:")
    print(f"  - {OUTPUT_PATH}")
    print(f"  - {ALT_OUTPUT_PATH}")

if __name__ == "__main__":
    sanitize_workflow()
