#!/usr/bin/env python3
"""
Test Suite for Dynamic Schema Inference & Onboarding Pipeline
Runs Node.js tests against schema_inference_node.js using dirty dataset files.
"""

import os
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_SCRIPT = os.path.join(BASE_DIR, "scripts", "schema_inference_node.js")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

def test_inference_with_node():
    print("=" * 80)
    print("TESTING DYNAMIC SCHEMA INFERENCE & ONBOARDING (Node.js)")
    print("=" * 80)

    # Test with dim_customer.csv and fact_sales_monthly.csv
    test_files = ["dim_customer.csv", "fact_sales_monthly.csv"]

    test_js = f"""
    const fs = require('fs');
    const path = require('path');
    const {{ processUploadedDataset }} = require({json.dumps(NODE_SCRIPT)});

    const files = {json.dumps(test_files)};
    const dataDir = {json.dumps(RAW_DATA_DIR)};

    for (const f of files) {{
        const fullPath = path.join(dataDir, f);
        const content = fs.readFileSync(fullPath, 'utf8');
        const result = processUploadedDataset(f, content);
        console.log('\\n------------------------------------------------------------');
        console.log('Processed File:', f);
        console.log('Inferred Table Name:', result.table_name);
        console.log('Inferred Columns & Types:', JSON.stringify(result.inferred_types, null, 2));
        console.log('Total Parsed Rows:', result.total_rows);
        console.log('Generated DDL Preview:');
        console.log(result.create_table_ddl);
    }}
    console.log('\\n[PASS] Dynamic Schema Inference successfully processed all test datasets.');
    """

    node_cmd = ["node", "-e", test_js]
    res = subprocess.run(node_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Test failed with error:")
        print(res.stderr)
        raise RuntimeError("Node inference test failed")
    
    print(res.stdout)
    print("=" * 80)
    print("DYNAMIC INGESTION VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    test_inference_with_node()
