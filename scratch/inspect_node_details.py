import json

with open("data_governor_n8n_template.json", "r", encoding="utf-8") as f:
    wf = json.load(f)

with open("scratch/template_node_summary.md", "w", encoding="utf-8") as out:
    out.write(f"# n8n Template Inspection: {wf.get('name')}\n\n")
    for i, node in enumerate(wf.get("nodes", [])):
        name = node.get("name")
        ntype = node.get("type")
        params = node.get("parameters", {})
        credentials = node.get("credentials", {})
        out.write(f"## {i}: {name} (`{ntype}`)\n")
        if credentials:
            out.write(f"- **Credentials**: `{list(credentials.keys())}`\n")
        for k, v in params.items():
            if isinstance(v, str) and len(v) > 300:
                out.write(f"- **{k}**: `{v[:300]}...` (length {len(v)})\n")
            elif isinstance(v, (dict, list)):
                dumped = json.dumps(v, indent=2)
                if len(dumped) > 400:
                    out.write(f"- **{k}**: \n```json\n{dumped[:400]}...\n```\n")
                else:
                    out.write(f"- **{k}**: \n```json\n{dumped}\n```\n")
            else:
                out.write(f"- **{k}**: `{v}`\n")
        out.write("\n---\n")

print("Generated scratch/template_node_summary.md successfully.")
