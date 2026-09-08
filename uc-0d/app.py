#!/usr/bin/env python3
"""
UC-0D: Civic Budget Allocation Application
Enforces Dual-Signature governance and prevents budget overdrafts.
"""

import os
import sys
import csv
import argparse
from typing import Dict, List, Tuple

INITIAL_WARD_BALANCES: Dict[str, float] = {
    "Ward-1": 15000000.0,
    "Ward-2": 8500000.0,
    "Ward-3": 22000000.0,
    "Ward-4": 4200000.0,
    "Ward-5": 11000000.0,
}

APPROVER_MAP = {
    "AUTH-WARD-01": "Ward Officer",
    "AUTH-FIN-01": "Finance Controller",
    "AUTH-COMM-01": "Municipal Commissioner",
    "AUTH-ENG-01": "Chief Engineer",
}


class BudgetController:
    def __init__(self, balances: Dict[str, float]):
        self.balances = balances.copy()

    def get_ward_balance(self, ward_id: str) -> float:
        return self.balances.get(ward_id, 0.0)

    def verify_signoff(self, approver_ids: List[str], amount: float) -> Tuple[bool, str]:
        roles = [APPROVER_MAP.get(a.strip()) for a in approver_ids if a.strip() in APPROVER_MAP]
        
        if amount > 100000.0:
            has_ward_officer = "Ward Officer" in roles
            has_fin_controller = "Finance Controller" in roles
            
            if has_ward_officer and has_fin_controller:
                return True, "Dual-signoff verified (Ward Officer + Finance Controller)"
            missing = []
            if not has_ward_officer:
                missing.append("Ward Officer (AUTH-WARD-01)")
            if not has_fin_controller:
                missing.append("Finance Controller (AUTH-FIN-01)")
            return False, f"INSUFFICIENT_SIGNATURES: missing {', '.join(missing)}"
        else:
            if roles:
                return True, f"Single sign-off valid for <= 100k ({roles[0]})"
            return False, "INSUFFICIENT_SIGNATURES: no recognized approver"

    def process_project(self, row: dict) -> dict:
        project_id = row["project_id"]
        ward_id = row["ward_id"]
        project_name = row["project_name"]
        requested_amount = float(row["requested_amount_inr"])
        approvers = [a.strip() for a in row.get("approvers", "").split(";") if a.strip()]

        current_balance = self.get_ward_balance(ward_id)
        valid_signoff, signoff_reason = self.verify_signoff(approvers, requested_amount)

        if not valid_signoff:
            return {
                "project_id": project_id,
                "ward_id": ward_id,
                "project_name": project_name,
                "requested_amount_inr": requested_amount,
                "status": "REJECTED",
                "allocated_amount_inr": 0.0,
                "remaining_ward_balance": current_balance,
                "audit_reason": signoff_reason,
            }

        if requested_amount > current_balance:
            return {
                "project_id": project_id,
                "ward_id": ward_id,
                "project_name": project_name,
                "requested_amount_inr": requested_amount,
                "status": "REJECTED",
                "allocated_amount_inr": 0.0,
                "remaining_ward_balance": current_balance,
                "audit_reason": f"EXCEEDS_WARD_BALANCE: required {requested_amount:,.2f} > available {current_balance:,.2f}",
            }

        # Commit expenditure
        self.balances[ward_id] -= requested_amount
        new_balance = self.balances[ward_id]

        return {
            "project_id": project_id,
            "ward_id": ward_id,
            "project_name": project_name,
            "requested_amount_inr": requested_amount,
            "status": "APPROVED",
            "allocated_amount_inr": requested_amount,
            "remaining_ward_balance": new_balance,
            "audit_reason": f"Approved and allocated. {signoff_reason}",
        }


def run_pipeline(input_csv: str, output_csv: str):
    controller = BudgetController(INITIAL_WARD_BALANCES)
    results = []

    with open(input_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            res = controller.process_project(row)
            results.append(res)

    fieldnames = [
        "project_id",
        "ward_id",
        "project_name",
        "requested_amount_inr",
        "status",
        "allocated_amount_inr",
        "remaining_ward_balance",
        "audit_reason",
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Processed {len(results)} projects. Results written to {output_csv}")
    for r in results:
        status_symbol = "[APPROVED]" if r["status"] == "APPROVED" else "[REJECTED]"
        print(f"  {status_symbol} {r['project_id']} ({r['ward_id']}): {r['status']} - {r['audit_reason']}")


def main():
    parser = argparse.ArgumentParser(description="UC-0D Civic Budget Allocator")
    parser.add_argument("--input", default="../data/budget/ward_projects.csv", help="Path to ward_projects.csv")
    parser.add_argument("--output", default="allocated_projects.csv", help="Path for output CSV")
    args = parser.parse_args()

    # Resolve relative paths
    input_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.input)) if not os.path.isabs(args.input) else args.input
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.output)) if not os.path.isabs(args.output) else args.output

    run_pipeline(input_path, output_path)


if __name__ == "__main__":
    main()
