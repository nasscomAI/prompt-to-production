#!/usr/bin/env python3
"""
Automated Evaluation Benchmark Harness
Vibe Coding / Prompt to Production / RAG-to-MCP Workshop

Runs automated verification across UC-0A, UC-0B, UC-0C, UC-0D, and UC-X.
"""

import os
import sys
import csv
import json
import glob
from typing import Dict, Any, List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

ALLOWED_CATEGORIES = {
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
}


# ─────────────────────────────────────────────────────────────────────────────
# UC-0A EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────

def eval_uc_0a() -> Dict[str, Any]:
    uc_dir = os.path.join(REPO_ROOT, "uc-0a")
    result_files = glob.glob(os.path.join(uc_dir, "results_*.csv"))

    if not result_files:
        return {"passed": False, "score": 0, "message": "No results_*.csv found in uc-0a/"}

    total_rows = 0
    severity_triggered = 0
    severity_correct = 0
    taxonomy_violations = 0
    missing_reasons = 0

    for fpath in result_files:
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_rows += 1
                desc = row.get("description", "").lower()
                cat = row.get("category", "")
                priority = row.get("priority", "")
                reason = row.get("reason", "")

                if cat not in ALLOWED_CATEGORIES:
                    taxonomy_violations += 1

                if not reason.strip():
                    missing_reasons += 1

                has_keyword = any(k in desc for k in SEVERITY_KEYWORDS)
                if has_keyword:
                    severity_triggered += 1
                    if priority.strip().lower() == "urgent":
                        severity_correct += 1

    sev_rate = (severity_correct / severity_triggered * 100) if severity_triggered else 100
    passed = (sev_rate == 100.0) and (taxonomy_violations == 0) and (missing_reasons == 0)

    return {
        "passed": passed,
        "files_checked": [os.path.basename(f) for f in result_files],
        "total_rows": total_rows,
        "severity_accuracy": f"{sev_rate:.1f}% ({severity_correct}/{severity_triggered})",
        "taxonomy_violations": taxonomy_violations,
        "missing_reasons": missing_reasons,
    }


# ─────────────────────────────────────────────────────────────────────────────
# UC-0B EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────

def eval_uc_0b() -> Dict[str, Any]:
    summary_path = os.path.join(REPO_ROOT, "uc-0b", "summary_hr_leave.txt")
    if not os.path.exists(summary_path):
        return {"passed": False, "message": "summary_hr_leave.txt not found in uc-0b/"}

    with open(summary_path, "r", encoding="utf-8") as f:
        content = f.read().lower()

    # Must preserve dual approval condition (Dept Head AND HR Director)
    has_dept_head = "department head" in content or "dept head" in content
    has_hr_director = "hr director" in content or "director" in content
    has_both_approvers = has_dept_head and has_hr_director

    passed = has_both_approvers and len(content) > 50

    return {
        "passed": passed,
        "preserved_clause_5_2_dual_approval": has_both_approvers,
        "file_length_chars": len(content),
    }


# ─────────────────────────────────────────────────────────────────────────────
# UC-0C EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────

def eval_uc_0c() -> Dict[str, Any]:
    csv_path = os.path.join(REPO_ROOT, "uc-0c", "growth_output.csv")
    if not os.path.exists(csv_path):
        return {"passed": False, "message": "growth_output.csv not found in uc-0c/"}

    rows = []
    has_null = False
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            for v in row.values():
                if v is None or v.strip().lower() in ["nan", "null", "none", ""]:
                    has_null = True

    # Must be segmented by ward (more than 1 row) and zero unhandled nulls
    passed = len(rows) > 1 and not has_null

    return {
        "passed": passed,
        "row_count": len(rows),
        "is_per_ward_segmented": len(rows) > 1,
        "contains_unhandled_nulls": has_null,
    }


# ─────────────────────────────────────────────────────────────────────────────
# UC-0D EVALUATOR
# ─────────────────────────────────────────────────────────────────────────────

def eval_uc_0d() -> Dict[str, Any]:
    csv_path = os.path.join(REPO_ROOT, "uc-0d", "allocated_projects.csv")
    if not os.path.exists(csv_path):
        return {"passed": False, "message": "allocated_projects.csv not found in uc-0d/"}

    rejections = {}
    approvals = {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["project_id"]
            status = row["status"]
            if status == "REJECTED":
                rejections[pid] = row.get("audit_reason", "")
            elif status == "APPROVED":
                approvals[pid] = row.get("allocated_amount_inr", 0)

    # PRJ-003, PRJ-004 (missing signatures) and PRJ-006 (overdraft) must be rejected
    expected_rejections = ["PRJ-2026-003", "PRJ-2026-004", "PRJ-2026-006"]
    correctly_rejected = all(pid in rejections for pid in expected_rejections)

    passed = correctly_rejected and len(approvals) >= 4

    return {
        "passed": passed,
        "total_approved": len(approvals),
        "total_rejected": len(rejections),
        "correctly_blocked_governance_traps": correctly_rejected,
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN HARNESS RUNNER
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("        CIVIC AI WORKSHOP - EVALUATION BENCHMARK HARNESS        ")
    print("=" * 65)

    modules = [
        ("UC-0A: Complaint Classifier", eval_uc_0a),
        ("UC-0B: Summary That Changes Meaning", eval_uc_0b),
        ("UC-0C: Number That Looks Right", eval_uc_0c),
        ("UC-0D: Budget Allocation & Dual-Signoff", eval_uc_0d),
    ]

    total_passed = 0
    total_modules = len(modules)

    for name, fn in modules:
        print(f"\nEvaluating {name}...")
        try:
            res = fn()
            status = "[PASS]" if res.get("passed") else "[FAIL]"
            if res.get("passed"):
                total_passed += 1
            print(f"  Status: {status}")
            for k, v in res.items():
                if k != "passed":
                    print(f"  - {k}: {v}")
        except Exception as e:
            print(f"  Status: [ERROR] -> {e}")

    print("\n" + "=" * 65)
    print(f"FINAL RESULT: {total_passed}/{total_modules} MODULES PASSED")
    print("=" * 65)

    if total_passed == total_modules:
        print("All modules meet production governance & enforcement standards!")
    else:
        print("Some modules require enforcement refinement. Review failures above.")


if __name__ == "__main__":
    main()
