#!/usr/bin/env python3
"""
Test client for Civic MCP Server.
Simulates an MCP host (like Cursor, Claude Desktop, or Antigravity) connecting over stdio.
"""

import sys
import subprocess
import json
import os

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "server.py")


def run_test():
    print("=== Testing Civic MCP Server over stdio ===")
    
    # Launch server process
    proc = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_recv(req: dict) -> dict:
        req_str = json.dumps(req) + "\n"
        proc.stdin.write(req_str)
        proc.stdin.flush()
        resp_line = proc.stdout.readline()
        return json.loads(resp_line)

    try:
        # 1. Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        }
        init_resp = send_recv(init_req)
        print(f"\n[1] Initialize response:")
        print(json.dumps(init_resp, indent=2))
        assert "serverInfo" in init_resp.get("result", {})

        # 2. List tools
        list_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        list_resp = send_recv(list_req)
        tools = list_resp.get("result", {}).get("tools", [])
        print(f"\n[2] Tools listed ({len(tools)} tools):")
        for t in tools:
            print(f"  - {t['name']}: {t['description'][:60]}...")
        assert len(tools) >= 5

        # 3. Call tool: get_ward_budget
        call_budget_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_ward_budget",
                "arguments": {"ward_id": "Ward-1"}
            }
        }
        call_budget_resp = send_recv(call_budget_req)
        print(f"\n[3] Call get_ward_budget('Ward-1'):")
        print(json.dumps(call_budget_resp, indent=2))

        # 4. Call tool: verify_expenditure_signoff (missing approval trap)
        call_signoff_req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "verify_expenditure_signoff",
                "arguments": {
                    "approver_ids": ["AUTH-WARD-01"],  # Missing Finance Controller
                    "amount": 250000.0
                }
            }
        }
        call_signoff_resp = send_recv(call_signoff_req)
        print(f"\n[4] Call verify_expenditure_signoff with missing Finance Controller (Amount: 250,000):")
        print(json.dumps(call_signoff_resp, indent=2))

        # 5. Call tool: fetch_policy_section
        call_policy_req = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "fetch_policy_section",
                "arguments": {
                    "policy_name": "policy_hr_leave",
                    "section_query": "5.2"
                }
            }
        }
        call_policy_resp = send_recv(call_policy_req)
        print(f"\n[5] Call fetch_policy_section('policy_hr_leave', query='5.2'):")
        print(json.dumps(call_policy_resp, indent=2))

        print("\n[PASS] All MCP server protocol tests passed successfully!")

    finally:
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    run_test()
