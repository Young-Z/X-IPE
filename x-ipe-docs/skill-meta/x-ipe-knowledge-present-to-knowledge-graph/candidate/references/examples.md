# Present to Knowledge Graph — Connector Operation Examples

## Example 1: Push Ontology with Auto-Resolution

**Graph JSON file** (`ontology.json`):
```json
{
  "entities": [
    {"id": "cls-001", "type": "class", "slug": "web-framework"},
    {"id": "inst-001", "type": "instance", "name": "Flask"}
  ],
  "relations": [
    {"id": "rel-001", "type": "related_to", "source": "cls-001", "target": "cls-002"}
  ]
}
```

**Command:**
```bash
python3 scripts/graph_connector.py connect --graph-json ontology.json
```

Port resolves via `.x-ipe.yaml` → 5858 (default). Token resolves via `instance/.internal_token`.

**Output (stdout):**
```json
{
  "success": true,
  "operation": "connector",
  "result": {
    "callback_status": "delivered",
    "server_response": {"status_code": 200, "body": "{\"status\": \"ok\"}"},
    "port_used": 5858,
    "attempts": 1
  }
}
```

---

## Example 2: Explicit Port and Token

**Command:**
```bash
python3 scripts/graph_connector.py connect \
  --graph-json ontology.json \
  --port 9000 \
  --token "my-secret-token" \
  --query "Flask templating" \
  --scope "project-abc"
```

**Output:** Same structure as Example 1, with `port_used: 9000`.

---

## Example 3: Missing Graph File

**Command:**
```bash
python3 scripts/graph_connector.py connect --graph-json nonexistent.json
```

**Output (stderr):**
```json
{"success": false, "error": "GRAPH_JSON_NOT_FOUND", "message": "Graph JSON file not found: nonexistent.json"}
```

---

## Example 4: Server Not Running

**Command:**
```bash
python3 scripts/graph_connector.py connect --graph-json ontology.json --token test
```

**Output (stderr, after 2 retries):**
```json
{"success": false, "error": "CONNECTION_FAILED", "message": "Failed after 2 attempts. Last error: Connection refused"}
```

---

## Example 5: Auth Token Not Found

**Command (no --token, no env var, no .internal_token file):**
```bash
X_IPE_INTERNAL_TOKEN="" python3 scripts/graph_connector.py connect --graph-json ontology.json
```

**Output (stderr):**
```json
{"success": false, "error": "AUTH_TOKEN_NOT_FOUND", "message": "No auth token found. Checked: --token flag, $X_IPE_INTERNAL_TOKEN env var, instance/.internal_token file"}
```
