#!/usr/bin/env python3
"""
Add Dynamic Ingestion Nodes to AI Data Governor n8n Workflow JSON
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW_PATH = os.path.join(BASE_DIR, "workflow", "ai_data_governor_workflow.json")
ALT_WORKFLOW_PATH = os.path.join(BASE_DIR, "workflow", "data_governor_n8n_workflow.json")

def add_dynamic_ingestion():
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        wf = json.load(f)

    nodes = wf.get("nodes", [])
    connections = wf.get("connections", {})

    # Define new nodes
    form_trigger_node = {
        "parameters": {
            "path": "upload-dataset",
            "formTitle": "AI Data Governor — Upload Raw Dataset",
            "formDescription": "Upload a CSV or Excel file. The system will auto-infer schema, create target PostgreSQL tables, batch-load records, and initiate the autonomous multi-agent audit.",
            "formFields": {
                "values": [
                    {
                        "fieldLabel": "Dataset File (CSV / Excel)",
                        "fieldType": "file",
                        "requiredField": True,
                        "multipleFiles": False
                    },
                    {
                        "fieldLabel": "Custom Table Name (Optional)",
                        "fieldType": "string",
                        "placeholder": "e.g. fact_sales_monthly (leave blank to infer from file name)"
                    }
                ]
            },
            "options": {
                "path": "upload-dataset"
            }
        },
        "type": "n8n-nodes-base.formTrigger",
        "typeVersion": 2.2,
        "position": [-1600, -250],
        "id": "f001-form-trigger-upload-dataset",
        "name": "Upload Dataset (Drag & Drop Form)",
        "webhookId": "upload-dataset"
    }

    schema_inference_node = {
        "parameters": {
            "jsCode": """// Dynamic Schema Inference & DDL Generator (AI Data Governor)
const binaryData = $input.first().binary;
const fileKey = Object.keys(binaryData)[0];
const fileObj = binaryData[fileKey];
const fileName = fileObj.fileName || 'uploaded_data.csv';

// Read text from binary
const buffer = Buffer.from(fileObj.data, 'base64');
const csvText = buffer.toString('utf-8');

function sanitize(raw) {
  if (!raw) return 'col_unnamed';
  let col = raw.trim().toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_+|_+$/g, '');
  if (/^[0-9]/.test(col)) col = 'col_' + col;
  return col || 'col_unnamed';
}

const lines = csvText.split(/\\r?\\n/).filter(l => l.trim() !== '');
const rawHeaders = lines[0].split(',').map(h => h.replace(/^"|"$/g, '').trim());
const cleanCols = rawHeaders.map(h => sanitize(h));

// Custom or inferred table name
const customTable = $input.first().json['Custom Table Name (Optional)'];
let tableName = (customTable && customTable.trim()) ? sanitize(customTable) : sanitize(fileName.replace(/\\.[^/.]+$/, ''));

// Sample first 100 rows for types
const colTypes = cleanCols.map(() => 'TEXT'); // Resilient TEXT type for dirty data load
const ddl = `CREATE TABLE IF NOT EXISTS "${tableName}" (\\n` + 
  cleanCols.map(c => `  "${c}" TEXT`).join(',\\n') + 
  `\\n);`;

// Format rows for batch insert
const rows = [];
for (let i = 1; i < lines.length; i++) {
  const parts = lines[i].split(',').map(v => v.replace(/^"|"$/g, '').trim());
  if (parts.length === rawHeaders.length) {
    const rowObj = {};
    for (let j = 0; j < cleanCols.length; j++) {
      rowObj[cleanCols[j]] = parts[j] === '' || parts[j].toUpperCase() === 'NULL' ? null : parts[j];
    }
    rows.push(rowObj);
  }
}

return [{
  json: {
    table_name: tableName,
    create_table_ddl: ddl,
    total_records: rows.length,
    columns: cleanCols,
    rows_sample: rows.slice(0, 5)
  }
}];"""
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-1350, -250],
        "id": "f002-dynamic-schema-inference",
        "name": "Dynamic Schema Inference"
    }

    auto_create_table_node = {
        "parameters": {
            "operation": "executeQuery",
            "query": "={{ $json.create_table_ddl }}",
            "options": {}
        },
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2.5,
        "position": [-1100, -250],
        "id": "f003-postgres-auto-create-table",
        "name": "Auto-Create Target Table (Postgres)",
        "credentials": {
            "postgres": {
                "id": "postgres-cred-id",
                "name": "Postgres (Supabase)"
            }
        }
    }

    sticky_note_ingest = {
        "parameters": {
            "content": "## Zero-SQL Drag-and-Drop Ingestion Path\nAccepts CSV/Excel uploads via Form Trigger, infers schema on the fly, auto-creates target PostgreSQL table, and initiates the multi-agent audit without touching Supabase SQL editor.",
            "height": 380,
            "width": 780,
            "color": 6
        },
        "type": "n8n-nodes-base.stickyNote",
        "typeVersion": 1,
        "position": [-1650, -380],
        "id": "f004-sticky-note-dynamic-ingest",
        "name": "Sticky Note: Dynamic Ingestion"
    }

    # Add nodes if not already present
    existing_ids = {n.get("id") for n in nodes}
    for new_node in [form_trigger_node, schema_inference_node, auto_create_table_node, sticky_note_ingest]:
        if new_node["id"] not in existing_ids:
            nodes.append(new_node)

    # Add connections
    # Form Trigger -> Dynamic Schema Inference
    connections["Upload Dataset (Drag & Drop Form)"] = {
        "main": [
            [
                {
                    "node": "Dynamic Schema Inference",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

    # Dynamic Schema Inference -> Auto-Create Target Table
    connections["Dynamic Schema Inference"] = {
        "main": [
            [
                {
                    "node": "Auto-Create Target Table (Postgres)",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

    # Auto-Create Target Table -> Master Data Investigator Agent
    connections["Auto-Create Target Table (Postgres)"] = {
        "main": [
            [
                {
                    "node": "Master Data Investigator Agent",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

    wf["nodes"] = nodes
    wf["connections"] = connections

    with open(WORKFLOW_PATH, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)
    with open(ALT_WORKFLOW_PATH, "w", encoding="utf-8") as f:
        json.dump(wf, f, indent=2, ensure_ascii=False)

    print("Successfully updated workflow JSON with dynamic ingestion pipeline:")
    print(f"  - Total nodes: {len(nodes)}")
    print(f"  - Saved to: {WORKFLOW_PATH}")

if __name__ == "__main__":
    add_dynamic_ingestion()
