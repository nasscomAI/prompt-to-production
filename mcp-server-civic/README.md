# Civic MCP Server (Model Context Protocol)

A reference implementation of a **Model Context Protocol (MCP)** server for Civic Tech, Policy RAG, and Agentic Workflows.

This server enables LLM agents running in IDEs (Cursor, VS Code, Claude Desktop, Antigravity) or custom CLI agents to invoke standardized civic tools over standard JSON-RPC `stdio`.

---

## Tools Provided

| Tool Name | Parameters | Description |
|---|---|---|
| `lookup_citizen_complaints` | `city: str`, `limit: int` | Fetches raw citizen complaints from city CSV files. |
| `get_ward_budget` | `ward_id: str` | Retrieves allocated municipal funds and active budget status. |
| `verify_expenditure_signoff` | `approver_ids: list[str]`, `amount: float` | Enforces dual-signature compliance (Ward Officer + Finance Controller for > 100k INR). |
| `fetch_policy_section` | `policy_name: str`, `section_query: str` | Retrieves specific clauses/sections from policy documents. |
| `check_employee_compliance` | `employee_id: str` | Validates mandatory compliance status before granting access. |

---

## Configuration

### Cursor / Claude Desktop / Antigravity MCP Config

Add this entry to your `mcpServers` configuration (`claude_desktop_config.json` or `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "civic-tools": {
      "command": "python",
      "args": [
        "C:\\NASSCOM\\mcp-server-civic\\server.py"
      ]
    }
  }
}
```

---

## Testing the Server

Run the included stdio test client:

```bash
python test_client.py
```
