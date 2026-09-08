#!/usr/bin/env python3
"""
Civic MCP Server
Model Context Protocol (MCP) Server for Civic Tech & Policy Operations

Provides standard tools for:
- Citizen Complaint classification & lookup
- Ward Budget & Allocation verification
- Policy document & section retrieval
- Employee compliance status verification

Implements JSON-RPC 2.0 stdio protocol adhering to the MCP Specification.
"""

import sys
import json
import os
import csv
from typing import Dict, Any, List, Optional

SERVER_NAME = "civic-mcp-server"
SERVER_VERSION = "1.0.0"

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
POLICY_DIR = os.path.join(DATA_DIR, "policy-documents")
BUDGET_FILE = os.path.join(DATA_DIR, "budget", "ward_budget.csv")
CITY_FILES_DIR = os.path.join(DATA_DIR, "city-test-files")

# In-memory mock databases for budget state
WARD_BALANCES: Dict[str, float] = {
    "Ward-1": 15000000.0,
    "Ward-2": 8500000.0,
    "Ward-3": 22000000.0,
    "Ward-4": 4200000.0,
    "Ward-5": 11000000.0,
}

AUTHORITY_ROLES: Dict[str, str] = {
    "AUTH-WARD-01": "Ward Officer",
    "AUTH-FIN-01": "Finance Controller",
    "AUTH-COMM-01": "Municipal Commissioner",
    "AUTH-ENG-01": "Chief Engineer",
}


# ─────────────────────────────────────────────────────────────────────────────
# TOOL DEFINITIONS & SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "lookup_citizen_complaints",
        "description": "Retrieve citizen complaints for a given city (e.g., pune, hyderabad, kolkata, ahmedabad).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (pune, hyderabad, kolkata, ahmedabad)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to return (default 5)",
                    "default": 5,
                },
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_ward_budget",
        "description": "Query the available budget and expenditure limit for a civic ward.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ward_id": {
                    "type": "string",
                    "description": "Ward identifier (e.g. Ward-1, Ward-2, Ward-3)",
                }
            },
            "required": ["ward_id"],
        },
    },
    {
        "name": "verify_expenditure_signoff",
        "description": "Verify dual-signoff authorization for civic expenditure. Requires Ward Officer AND Finance Controller approval for amounts above 100,000 INR.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "approver_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of approver IDs (e.g., ['AUTH-WARD-01', 'AUTH-FIN-01'])",
                },
                "amount": {
                    "type": "number",
                    "description": "Proposed expenditure amount in INR",
                },
            },
            "required": ["approver_ids", "amount"],
        },
    },
    {
        "name": "fetch_policy_section",
        "description": "Fetch text from a specific policy document (policy_hr_leave, policy_it_acceptable_use, policy_finance_reimbursement).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "policy_name": {
                    "type": "string",
                    "description": "Policy document name without extension (e.g. policy_hr_leave, policy_it_acceptable_use, policy_finance_reimbursement)",
                },
                "section_query": {
                    "type": "string",
                    "description": "Optional section number or keyword to filter lines",
                    "default": "",
                },
            },
            "required": ["policy_name"],
        },
    },
    {
        "name": "check_employee_compliance",
        "description": "Check employee compliance acknowledgement status before granting access.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "employee_id": {
                    "type": "string",
                    "description": "Employee ID (e.g. EMP-2026-0847)",
                }
            },
            "required": ["employee_id"],
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# TOOL IMPLEMENTATIONS
# ─────────────────────────────────────────────────────────────────────────────

def handle_lookup_citizen_complaints(city: str, limit: int = 5) -> Dict[str, Any]:
    city_clean = city.strip().lower()
    csv_path = os.path.join(CITY_FILES_DIR, f"test_{city_clean}.csv")
    if not os.path.exists(csv_path):
        return {
            "error": f"City test file not found for '{city}'. Available cities: pune, hyderabad, kolkata, ahmedabad"
        }

    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)

    return {"city": city_clean, "total_returned": len(rows), "complaints": rows}


def handle_get_ward_budget(ward_id: str) -> Dict[str, Any]:
    ward_key = ward_id.strip()
    if ward_key in WARD_BALANCES:
        return {
            "ward_id": ward_key,
            "allocated_budget_inr": WARD_BALANCES[ward_key],
            "status": "ACTIVE",
            "requires_dual_signoff_above": 100000.0,
        }
    return {
        "error": f"Ward '{ward_id}' not found. Available wards: {list(WARD_BALANCES.keys())}"
    }


def handle_verify_expenditure_signoff(approver_ids: List[str], amount: float) -> Dict[str, Any]:
    approver_roles = [AUTHORITY_ROLES.get(a) for a in approver_ids if a in AUTHORITY_ROLES]
    has_ward_officer = "Ward Officer" in approver_roles
    has_fin_controller = "Finance Controller" in approver_roles

    if amount > 100000.0:
        if has_ward_officer and has_fin_controller:
            return {
                "authorized": True,
                "amount": amount,
                "approvers": approver_roles,
                "status": "APPROVED",
                "message": "Dual sign-off verified (Ward Officer + Finance Controller).",
            }
        else:
            missing = []
            if not has_ward_officer:
                missing.append("Ward Officer")
            if not has_fin_controller:
                missing.append("Finance Controller")
            return {
                "authorized": False,
                "amount": amount,
                "status": "REJECTED_INSUFFICIENT_AUTHORIZATION",
                "missing_approvals": missing,
                "message": f"Expenditure exceeds 100,000 INR. Missing required approvals: {', '.join(missing)}",
            }
    else:
        # Under 100k requires at least one recognized official
        if approver_roles:
            return {
                "authorized": True,
                "amount": amount,
                "approvers": approver_roles,
                "status": "APPROVED",
                "message": "Single sign-off valid for expenditures under 100,000 INR.",
            }
        return {
            "authorized": False,
            "amount": amount,
            "status": "REJECTED_UNKNOWN_APPROVER",
            "message": "No recognized approver provided.",
        }


def handle_fetch_policy_section(policy_name: str, section_query: str = "") -> Dict[str, Any]:
    clean_name = policy_name.replace(".txt", "").strip()
    file_path = os.path.join(POLICY_DIR, f"{clean_name}.txt")
    if not os.path.exists(file_path):
        return {
            "error": f"Policy '{policy_name}' not found. Available: policy_hr_leave, policy_it_acceptable_use, policy_finance_reimbursement"
        }

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if section_query:
        lines = content.split("\n")
        matched = [line for line in lines if section_query.lower() in line.lower()]
        return {
            "policy": clean_name,
            "query": section_query,
            "matching_lines": matched if matched else ["No matching lines found."],
        }

    return {"policy": clean_name, "content": content}


def handle_check_employee_compliance(employee_id: str) -> Dict[str, Any]:
    compliance_file = os.path.join(REPO_ROOT, "onboarding-agent", "data", "compliance_state.json")
    if os.path.exists(compliance_file):
        with open(compliance_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            if employee_id in db:
                return db[employee_id]

    # Default mock response
    return {
        "employee_id": employee_id,
        "overall_status": "CLEARED" if "0847" not in employee_id else "PENDING",
        "code_of_conduct": "ACKNOWLEDGED",
        "data_handling_policy": "ACKNOWLEDGED",
        "security_guidelines": "ACKNOWLEDGED",
        "posh_training": "ACKNOWLEDGED",
    }


# ─────────────────────────────────────────────────────────────────────────────
# JSON-RPC DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    if name == "lookup_citizen_complaints":
        return handle_lookup_citizen_complaints(
            city=arguments.get("city", "pune"),
            limit=int(arguments.get("limit", 5)),
        )
    elif name == "get_ward_budget":
        return handle_get_ward_budget(ward_id=arguments.get("ward_id", ""))
    elif name == "verify_expenditure_signoff":
        return handle_verify_expenditure_signoff(
            approver_ids=arguments.get("approver_ids", []),
            amount=float(arguments.get("amount", 0.0)),
        )
    elif name == "fetch_policy_section":
        return handle_fetch_policy_section(
            policy_name=arguments.get("policy_name", ""),
            section_query=arguments.get("section_query", ""),
        )
    elif name == "check_employee_compliance":
        return handle_check_employee_compliance(employee_id=arguments.get("employee_id", ""))
    else:
        raise ValueError(f"Unknown tool: {name}")


def process_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            result = call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {}
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


def main():
    """Main stdio loop for MCP server."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = process_message(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON"}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
