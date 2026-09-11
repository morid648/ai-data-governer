import json

with open('data_governor_n8n_template.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Workflow name:", d.get("name"))
nodes = d.get("nodes", [])
print(f"Total nodes: {len(nodes)}")
for i, n in enumerate(nodes):
    print(f"{i}: {n.get('name')} [{n.get('type')}] id={n.get('id')}")

print("\nConnections summary:")
for k, v in d.get("connections", {}).items():
    print(f"  From {k} -> {list(v.keys())}")
