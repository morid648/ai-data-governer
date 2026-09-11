# n8n Template Inspection: 0_Main

## 0: When clicking ‘Execute workflow’ (`n8n-nodes-base.manualTrigger`)

---
## 1: Split Out (`n8n-nodes-base.splitOut`)
- **fieldToSplitOut**: `output`
- **options**: 
```json
{}
```

---
## 2: Merge (`n8n-nodes-base.merge`)
- **mode**: `combine`
- **advanced**: `True`
- **mergeByFields**: 
```json
{
  "values": [
    {
      "field1": "issue_id",
      "field2": "output[0].issue_id"
    }
  ]
}
```
- **joinMode**: `enrichInput1`
- **options**: 
```json
{}
```

---
## 3: Structured Output Parser2 (`@n8n/n8n-nodes-langchain.outputParserStructured`)
- **schemaType**: `manual`
- **inputSchema**: `{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "issue_id": {
        "type": "string",
        "pattern": "^ISSUE-\\d{3}$"
      },
      "category": {
        "type": "string",
        "enum": [
          "Fi...` (length 871)

---
## 4: Loop Over Items (`n8n-nodes-base.splitInBatches`)
- **options**: 
```json
{}
```

---
## 5: Structured Output Parser1 (`@n8n/n8n-nodes-langchain.outputParserStructured`)
- **schemaType**: `manual`
- **inputSchema**: `{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "issue_id": {
        "type": "string",
        "pattern": "^ISSUE-\\d{3}$"
      },
      "status": {
        "type": "string",
        "enum": ["resolved", "fai...` (length 539)

---
## 6: Aggregate (`n8n-nodes-base.aggregate`)
- **aggregate**: `aggregateAllItemData`
- **options**: 
```json
{}
```

---
## 7: Structured Output Parser3 (`@n8n/n8n-nodes-langchain.outputParserStructured`)
- **schemaType**: `manual`
- **inputSchema**: `{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "report_title": { "type": "string" },
    "report_link": { "type": "string" }
  },
  "required": ["report_title", "report_link"],
  "additionalProperties": false
}
`

---
## 8: Data Issue Fixer Agent (`@n8n/n8n-nodes-langchain.agent`)
- **promptType**: `define`
- **text**: `=Here is the issue details

Issue ID - {{ $('Loop Over Items').item.json.json.issue_id }}

Category - {{ $('Loop Over Items').item.json.json.category }}

Description - {{ $('Loop Over Items').item.json.json.description }}

Sample values: {{ $('Loop Over Items').item.json.json.sample_values }}

Sugge...` (length 361)
- **hasOutputParser**: `True`
- **options**: 
```json
{
  "systemMessage": "=You are an SQL Generator & Executor Agent, responsible for automatically fixing data\u2011quality issues in a PostgreSQL database.\n\n1\u00b7Input  \nReceive the following details as input:  \n \u2022\u202fissue_id     \n \u2022\u202fcategory       \n \u2022\u202fdescription     \n \u2022\u202fsample_data  \n \u2022\u202fsuggestion    \n\n2\u00b7Processing Steps  \n \u2022 *...
```

---
## 9: Groq-Kimi-K2 (`@n8n/n8n-nodes-langchain.lmChatGroq`)
- **Credentials**: `['groqApi']`
- **model**: `moonshotai/kimi-k2-instruct`
- **options**: 
```json
{}
```

---
## 10: Gemini-2.5-Flash (`@n8n/n8n-nodes-langchain.lmChatGoogleGemini`)
- **Credentials**: `['googlePalmApi']`
- **options**: 
```json
{}
```

---
## 11: Gemini-2.5-Flash1 (`@n8n/n8n-nodes-langchain.lmChatGoogleGemini`)
- **Credentials**: `['googlePalmApi']`
- **options**: 
```json
{}
```

---
## 12: Create Google Docs (`n8n-nodes-base.googleDocsTool`)
- **Credentials**: `['googleDocsOAuth2Api']`
- **descriptionType**: `manual`
- **toolDescription**: `Use this tool to create a new Google Docs`
- **folderId**: `1gOOJvm8EvLDAyOrmSvn6VYmIuog7A38F`
- **title**: `={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Title', ``, 'string') }}`

---
## 13: Update Access (`n8n-nodes-base.googleDriveTool`)
- **Credentials**: `['googleDriveOAuth2Api']`
- **descriptionType**: `manual`
- **toolDescription**: `Use this tool to share the access of the document to everyone`
- **operation**: `share`
- **fileId**: 
```json
{
  "__rl": true,
  "value": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('File', ``, 'string') }}",
  "mode": "id"
}
```
- **permissionsUi**: 
```json
{
  "permissionsValues": {
    "role": "reader",
    "type": "anyone"
  }
}
```
- **options**: 
```json
{}
```

---
## 14: Update Google Docs (`n8n-nodes-base.googleDocsTool`)
- **Credentials**: `['googleDocsOAuth2Api']`
- **descriptionType**: `manual`
- **toolDescription**: `Use this tool update the content in the google docs`
- **operation**: `update`
- **documentURL**: `={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Doc_ID_or_URL', ``, 'string') }}`
- **actionsUi**: 
```json
{
  "actionFields": [
    {
      "action": "insert",
      "text": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('actionFields0_Text', ``, 'string') }}"
    },
    {
      "object": "footer",
      "action": "create",
      "insertSegment": "footer",
      "segmentId": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('actionFields1_Segment_ID', ``, 'string') }}",
      "index": "={{ /*n8...
```

---
## 15: Query Tool (`@n8n/n8n-nodes-langchain.toolWorkflow`)
- **description**: `Call this tool to execute the generated Postgres SQL query and get the data`
- **workflowId**: 
```json
{
  "__rl": true,
  "value": "P8xLBRRw2OIW2hXQ",
  "mode": "list",
  "cachedResultName": "SQL Query executor"
}
```
- **workflowInputs**: 
```json
{
  "mappingMode": "defineBelow",
  "value": {
    "sql_query": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('sql_query', ``, 'string') }}"
  },
  "matchingColumns": [
    "sql_query"
  ],
  "schema": [
    {
      "id": "sql_query",
      "displayName": "sql_query",
      "required": false,
      "defaultMatch": false,
      "display": true,
      "canBeUsedToMatch": true,
      "type": "s...
```

---
## 16: Postgres Schema (`n8n-nodes-base.postgresTool`)
- **Credentials**: `['postgres']`
- **descriptionType**: `manual`
- **toolDescription**: `Use this tool to get the Table Schema details`
- **operation**: `executeQuery`
- **query**: `SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_schema = 'public' -- Or your specific schema name
ORDER BY
    table_name,
    ordinal_position;`
- **options**: 
```json
{}
```

---
## 17: Query Tool1 (`@n8n/n8n-nodes-langchain.toolWorkflow`)
- **description**: `Call this tool to execute the generated Postgres SQL query and get the data`
- **workflowId**: 
```json
{
  "__rl": true,
  "value": "P8xLBRRw2OIW2hXQ",
  "mode": "list",
  "cachedResultName": "SQL Query executor"
}
```
- **workflowInputs**: 
```json
{
  "mappingMode": "defineBelow",
  "value": {
    "sql_query": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('sql_query', ``, 'string') }}"
  },
  "matchingColumns": [
    "sql_query"
  ],
  "schema": [
    {
      "id": "sql_query",
      "displayName": "sql_query",
      "required": false,
      "defaultMatch": false,
      "display": true,
      "canBeUsedToMatch": true,
      "type": "s...
```

---
## 18: Postgres_Schmea (`n8n-nodes-base.postgresTool`)
- **Credentials**: `['postgres']`
- **descriptionType**: `manual`
- **toolDescription**: `Use this tool to get the Table Schema details`
- **operation**: `executeQuery`
- **query**: `SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_schema = 'public' -- Or your specific schema name
ORDER BY
    table_name,
    ordinal_position;`
- **options**: 
```json
{}
```

---
## 19: Send Approval Request and Wait (`n8n-nodes-base.gmail`)
- **Credentials**: `['gmailOAuth2']`
- **operation**: `sendAndWait`
- **sendTo**: `tony.sharmacodebasics@gmail.com`
- **subject**: `=Approval Needed – Data Quality Fix ({{ $json.json.issue_id }})`
- **message**: `=Tony,

We’ve detected a data‑quality issue in the AtliQ database:

Issue ID - {{ $json.json.issue_id }}

Description - {{ $json.json.description }}

Suggestion: {{ $json.json.suggestion }}

We plan to apply this fix via SQL. Please review and let us know if you approve so we can proceed.

Regards,
...` (length 310)
- **approvalOptions**: 
```json
{
  "values": {
    "approvalType": "double"
  }
}
```
- **options**: 
```json
{
  "appendAttribution": true
}
```

---
## 20: Sticky Note (`n8n-nodes-base.stickyNote`)
- **content**: `## #1 -  Investigate the Database and list down the issues 
`
- **height**: `544`
- **width**: `592`
- **color**: `3`

---
## 21: Sticky Note1 (`n8n-nodes-base.stickyNote`)
- **content**: `## #2 - Fix the issues using SQL
`
- **height**: `496`
- **width**: `880`
- **color**: `4`

---
## 22: Approved? (`n8n-nodes-base.if`)
- **conditions**: 
```json
{
  "options": {
    "caseSensitive": true,
    "leftValue": "",
    "typeValidation": "strict",
    "version": 2
  },
  "conditions": [
    {
      "id": "88539708-4ba7-4ea3-bedd-44d67f3b7075",
      "leftValue": "={{ $json.data.approved }}",
      "rightValue": "",
      "operator": {
        "type": "boolean",
        "operation": "true",
        "singleValue": true
      }
    }
  ],
  "combin...
```
- **options**: 
```json
{}
```

---
## 23: Sticky Note2 (`n8n-nodes-base.stickyNote`)
- **content**: `## #3 - Create a Report`
- **height**: `480`
- **width**: `768`
- **color**: `5`

---
## 24: Send Approval Request and Wait1 (`n8n-nodes-base.gmail`)
- **Credentials**: `['gmailOAuth2']`
- **operation**: `sendAndWait`
- **sendTo**: `tony.sharmacodebasics@gmail.com`
- **subject**: `=Data Quality Fixs - Need your 10 Mins`
- **message**: `=Tony,

We’ve identified {{ $('Can be fixed with SQL?').all().length }} data-quality issues in the AtliQ database that we plan to fix using SQL.

We'll share the list of issues along with the proposed changes. Once you review them, we’ll move forward with the fixes based on your approval.

It’ll tak...` (length 500)
- **approvalOptions**: 
```json
{
  "values": {
    "approvalType": "double",
    "approveLabel": "YES",
    "disapproveLabel": "NO"
  }
}
```
- **options**: 
```json
{
  "appendAttribution": true
}
```

---
## 25: If (`n8n-nodes-base.if`)
- **conditions**: 
```json
{
  "options": {
    "caseSensitive": true,
    "leftValue": "",
    "typeValidation": "strict",
    "version": 2
  },
  "conditions": [
    {
      "id": "009557b2-3359-4095-b34c-89cc4581687e",
      "leftValue": "={{ $json.data.approved }}",
      "rightValue": "",
      "operator": {
        "type": "boolean",
        "operation": "true",
        "singleValue": true
      }
    }
  ],
  "combin...
```
- **options**: 
```json
{}
```

---
## 26: Edit Fields (`n8n-nodes-base.set`)
- **assignments**: 
```json
{
  "assignments": [
    {
      "id": "41c08f5f-0ac6-4cab-a1f3-32f690336e58",
      "name": "issue_itmes",
      "value": "={{ $('Can be fixed with SQL?').all() }}",
      "type": "array"
    }
  ]
}
```
- **options**: 
```json
{}
```

---
## 27: Split Out1 (`n8n-nodes-base.splitOut`)
- **fieldToSplitOut**: `issue_itmes`
- **options**: 
```json
{}
```

---
## 28: Can be fixed with SQL? (`n8n-nodes-base.filter`)
- **conditions**: 
```json
{
  "options": {
    "caseSensitive": true,
    "leftValue": "",
    "typeValidation": "strict",
    "version": 2
  },
  "conditions": [
    {
      "id": "830bebba-f255-4b37-a7fb-775ca758a770",
      "leftValue": "={{ $json.category }}",
      "rightValue": "Fixable with SQL",
      "operator": {
        "type": "string",
        "operation": "equals",
        "name": "filter.operator.equals"
   ...
```
- **options**: 
```json
{}
```

---
## 29: No Operation, do nothing (`n8n-nodes-base.noOp`)

---
## 30: Sticky Note3 (`n8n-nodes-base.stickyNote`)
- **content**: `## Waiting for the Approver's time
`
- **height**: `656`
- **width**: `624`

---
## 31: Send a message (`n8n-nodes-base.gmail`)
- **Credentials**: `['gmailOAuth2']`
- **sendTo**: `tony.sharmacodebasics@gmail.com`
- **subject**: `=AtliQ {{ $json.output.report_title }}`
- **emailType**: `text`
- **message**: `=Tony,

We have completed the Health Check of our AtliQ DB.

And you can find the comprehensive report with further details in this document - {{ $json.output.report_link }}

Regards,
Data Checker Reporting Bot`
- **options**: 
```json
{}
```

---
## 32: Master Data Investigator Agent (`@n8n/n8n-nodes-langchain.agent`)
- **promptType**: `define`
- **text**: `Run a full data‑quality audit on the connected PostgreSQL database.`
- **hasOutputParser**: `True`
- **options**: 
```json
{
  "systemMessage": "=You are Master\u202fData\u202fHealth\u202fChecker, sentinel of data fidelity across a PostgreSQL landscape.\n\nYour mission is to:\n\nScan every reachable schema, table, and column using the provided query tool.\n\nDetect all possible data-quality issues.\n\nEmit only a clean JSON array\u2014nothing else.\n\n\ud83d\udd0d Evaluation Scope:\nCheck for all of the following:\n\n...
```

---
## 33: Data Investigation Reporter (`@n8n/n8n-nodes-langchain.agent`)
- **promptType**: `define`
- **text**: `={{ $json.toJsonString() }}`
- **hasOutputParser**: `True`
- **options**: 
```json
{
  "systemMessage": "=You are the Data Health\u202fReporter Agent, tasked with creating and delivering a polished database health\u2011check report via Google Docs and Drive.\n\n\ud83d\udce5 Input:\n\nReceive exactly one JSON object (no wrappers) with a top\u2011level key `\"data\"` whose value is an array of issue objects. Each issue object includes:\n\n- `issue_id`\n- `category` \n- `descriptio...
```

---
## 34: Sticky Note4 (`n8n-nodes-base.stickyNote`)
- **content**: `[![Codebasics Logo](https://files.codebasics.io/v3/images/sticky-logo.svg)](https://codebasics.io/) 
### AI Automation for Data Professionals Course 
`
- **height**: `192`
- **width**: `192`
- **color**: `5`

---
