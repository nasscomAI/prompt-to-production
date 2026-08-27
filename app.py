"""
UC-0C: Number That Looks Right — Budget Validator
===================================================
Agent   : BudgetGuard (see agents.md)
Skills  : SKILL-01 through SKILL-06 (see skills.md)
Input   : data/budget/ward_budget.csv
Output  : uc-0c/growth_output.csv

CRAFT loop commit message format:
  UC-0C Fix <what>: <why it failed> → <what you changed>

Run:
  python uc-0c/app.py
"""

import csv
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
BUDGET_CSV = REPO_ROOT / "data" / "budget" / "ward_budget.csv"
OUTPUT_CSV = Path(__file__).resolve().parent / "growth_output.csv"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = ["ward_id", "category", "allocated_amount", "fiscal_year"]
ROUNDING_TOLERANCE = 1.0   # ₹1 tolerance for float rounding

FLAG_OK = "OK"
FLAG_SCOPE = "SCOPE_VIOLATION"
FLAG_AGG = "AGGREGATION_ERROR"
FLAG_UTIL = "UTILISATION_ANOMALY"
FLAG_MISSING = "MISSING_DATA"


# ---------------------------------------------------------------------------
# SKILL-04: Missing Data Sentinel
# ---------------------------------------------------------------------------
def check_missing_data(row: dict) -> tuple[bool, str]:
    """Return (is_valid, reason). Checks all required fields are present."""
    for field in REQUIRED_FIELDS:
        val = row.get(field, "").strip()
        if val == "" or val is None:
            return False, f"Required field '{field}' is missing or empty."
    # allocated_amount must be numeric and non-negative
    try:
        alloc = float(row["allocated_amount"])
        if alloc < 0:
            return False, f"allocated_amount is negative ({alloc}), which is invalid."
    except ValueError:
        return False, f"allocated_amount '{row['allocated_amount']}' is not a valid number."
    return True, ""


# ---------------------------------------------------------------------------
# SKILL-03: Budget Utilisation Rate Validator
# ---------------------------------------------------------------------------
def check_utilisation(row: dict) -> tuple[str, float | None, str]:
    """
    Returns (flag, utilisation_pct, reason).
    Only runs when spent_amount is present.
    """
    spent_raw = row.get("spent_amount", "").strip()
    if spent_raw == "":
        return FLAG_OK, None, ""

    try:
        spent = float(spent_raw)
        alloc = float(row["allocated_amount"])
    except ValueError:
        return FLAG_AGG, None, (
            f"Ward {row['ward_id']}, {row['category']}: "
            f"spent_amount '{spent_raw}' is not a valid number."
        )

    if alloc == 0:
        if spent > 0:
            return FLAG_AGG, None, (
                f"Ward {row['ward_id']}, {row['category']}: "
                f"allocated_amount is 0 but spent_amount is {spent} — corrupt or placeholder row."
            )
        return FLAG_OK, 0.0, ""

    util_pct = (spent / alloc) * 100

    if util_pct > 100:
        return FLAG_UTIL, round(util_pct, 2), (
            f"Ward {row['ward_id']}, {row['category']}: "
            f"utilisation is {util_pct:.1f}% — spent (₹{spent:,.0f}) exceeds allocated (₹{alloc:,.0f})."
        )

    return FLAG_OK, round(util_pct, 2), ""


# ---------------------------------------------------------------------------
# SKILL-01 + SKILL-02: Aggregation & Scope Check
# ---------------------------------------------------------------------------
def build_lookup(rows: list[dict]) -> dict:
    """
    Build a lookup: (ward_id, category, fiscal_year) → allocated_amount
    Only non-summary rows are indexed.
    Summary rows are identified by is_summary == 'true' or '1'.
    """
    lookup: dict[tuple, float] = {}
    for r in rows:
        if r.get("is_summary", "").strip().lower() in ("true", "1", "yes"):
            continue
        key = (
            r["ward_id"].strip(),
            r["category"].strip(),
            r["fiscal_year"].strip(),
        )
        try:
            lookup[key] = lookup.get(key, 0.0) + float(r["allocated_amount"])
        except ValueError:
            pass
    return lookup


def check_scope_and_aggregation(row: dict, all_rows: list[dict]) -> tuple[str, float | None, str]:
    """
    SKILL-02: Validate scope — a summary row must span exactly 1 ward + 1 category.
    SKILL-01: Re-derive the total from source rows and compare.
    Only runs on rows where is_summary == true.
    """
    if row.get("is_summary", "").strip().lower() not in ("true", "1", "yes"):
        return FLAG_OK, None, ""

    ward = row["ward_id"].strip()
    category = row["category"].strip()
    fiscal_year = row["fiscal_year"].strip()
    reported = float(row["allocated_amount"])

    # Collect contributing source rows
    contributors = [
        r for r in all_rows
        if r.get("is_summary", "").strip().lower() not in ("true", "1", "yes")
        and r["fiscal_year"].strip() == fiscal_year
    ]

    # SKILL-02: Check scope — any contributor with different ward or category?
    scope_violations = [
        r for r in contributors
        if r["ward_id"].strip() != ward or r["category"].strip() != category
    ]
    if scope_violations:
        offending_wards = {r["ward_id"].strip() for r in scope_violations}
        offending_cats = {r["category"].strip() for r in scope_violations}
        return FLAG_SCOPE, None, (
            f"Ward {ward}, {category}: summary row pulls data from other wards "
            f"{offending_wards - {ward}} or categories {offending_cats - {category}} — scope violation."
        )

    # SKILL-01: Re-derive total from matching source rows
    matching = [
        r for r in contributors
        if r["ward_id"].strip() == ward and r["category"].strip() == category
    ]
    derived = sum(float(r["allocated_amount"]) for r in matching)

    if abs(derived - reported) > ROUNDING_TOLERANCE:
        return FLAG_AGG, round(derived, 2), (
            f"Ward {ward}, {category}: reported total ₹{reported:,.0f} "
            f"but re-derived total is ₹{derived:,.0f} — aggregation error of ₹{abs(derived - reported):,.0f}."
        )

    return FLAG_OK, round(derived, 2), ""


# ---------------------------------------------------------------------------
# SKILL-05: Growth Output Generator
# ---------------------------------------------------------------------------
def generate_growth_output(rows: list[dict]) -> list[dict]:
    """
    Computes YoY budget growth per (ward_id, category).
    Returns list of dicts for growth_output.csv.
    """
    # Group by (ward, category) → sorted list of (fiscal_year, allocated)
    from collections import defaultdict
    groups: dict[tuple, list[tuple]] = defaultdict(list)

    for r in rows:
        if r.get("is_summary", "").strip().lower() in ("true", "1", "yes"):
            continue
        try:
            alloc = float(r["allocated_amount"])
        except ValueError:
            alloc = None
        groups[(r["ward_id"].strip(), r["category"].strip())].append(
            (r["fiscal_year"].strip(), alloc)
        )

    # Sort each group by fiscal year
    for key in groups:
        groups[key].sort(key=lambda x: x[0])

    output_rows = []
    for (ward, category), entries in sorted(groups.items()):
        for i, (fy, alloc) in enumerate(entries):
            if i == 0:
                prev_alloc = None
                growth_pct = None
                growth_flag = "NEW"
            else:
                prev_fy, prev_alloc = entries[i - 1]
                if prev_alloc is None or alloc is None:
                    growth_pct = None
                    growth_flag = "MISSING_PRIOR"
                elif prev_alloc == 0:
                    growth_pct = None
                    growth_flag = "NEW"
                else:
                    growth_pct = round(((alloc - prev_alloc) / prev_alloc) * 100, 2)
                    if growth_pct > 0:
                        growth_flag = "GROWTH"
                    elif growth_pct < 0:
                        growth_flag = "DECLINE"
                    else:
                        growth_flag = "FLAT"

            output_rows.append({
                "ward_id": ward,
                "category": category,
                "fiscal_year": fy,
                "allocated_amount": alloc if alloc is not None else "",
                "prev_year_allocated": prev_alloc if prev_alloc is not None else "",
                "growth_pct": growth_pct if growth_pct is not None else "",
                "growth_flag": growth_flag,
            })

    return output_rows


# ---------------------------------------------------------------------------
# Main Validation Runner
# ---------------------------------------------------------------------------
def validate(budget_csv: Path) -> list[dict]:
    """
    Run the full SKILL-04 → SKILL-02 → SKILL-01 → SKILL-03 → SKILL-06 pipeline.
    Returns list of result dicts.
    """
    if not budget_csv.exists():
        print(f"[ERROR] Budget file not found: {budget_csv}")
        sys.exit(1)

    with open(budget_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader]

    if not rows:
        print("[ERROR] Budget CSV is empty.")
        sys.exit(1)

    results = []

    for row in rows:
        ward = row.get("ward_id", "?").strip()
        category = row.get("category", "?").strip()
        fiscal_year = row.get("fiscal_year", "?").strip()

        # ── SKILL-04: Missing Data ─────────────────────────────────────────
        ok, reason = check_missing_data(row)
        if not ok:
            results.append({
                "ward_id": ward,
                "category": category,
                "fiscal_year": fiscal_year,
                "reported_amount": row.get("allocated_amount", ""),
                "expected_amount": None,
                "utilisation_pct": None,
                "is_valid": False,
                "flag_type": FLAG_MISSING,
                "reason": reason,
            })
            continue

        # ── SKILL-02 + SKILL-01: Scope & Aggregation ──────────────────────
        flag, expected, reason = check_scope_and_aggregation(row, rows)
        if flag != FLAG_OK:
            results.append({
                "ward_id": ward,
                "category": category,
                "fiscal_year": fiscal_year,
                "reported_amount": row.get("allocated_amount", ""),
                "expected_amount": expected,
                "utilisation_pct": None,
                "is_valid": False,
                "flag_type": flag,
                "reason": reason,
            })
            continue

        # ── SKILL-03: Utilisation ──────────────────────────────────────────
        util_flag, util_pct, util_reason = check_utilisation(row)
        if util_flag != FLAG_OK:
            results.append({
                "ward_id": ward,
                "category": category,
                "fiscal_year": fiscal_year,
                "reported_amount": row.get("allocated_amount", ""),
                "expected_amount": None,
                "utilisation_pct": util_pct,
                "is_valid": False,
                "flag_type": util_flag,
                "reason": util_reason,
            })
            continue

        # ── All checks passed ──────────────────────────────────────────────
        results.append({
            "ward_id": ward,
            "category": category,
            "fiscal_year": fiscal_year,
            "reported_amount": row.get("allocated_amount", ""),
            "expected_amount": expected,
            "utilisation_pct": util_pct,
            "is_valid": True,
            "flag_type": FLAG_OK,
            "reason": "",
        })

    return results


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
def main():
    print(f"[BudgetGuard] Reading: {BUDGET_CSV}")
    results = validate(BUDGET_CSV)

    # ── Print summary ──────────────────────────────────────────────────────
    total = len(results)
    invalid = [r for r in results if not r["is_valid"]]
    flag_counts: dict[str, int] = {}
    for r in results:
        flag_counts[r["flag_type"]] = flag_counts.get(r["flag_type"], 0) + 1

    print(f"\n{'='*60}")
    print(f"  BudgetGuard Validation Report")
    print(f"{'='*60}")
    print(f"  Total rows     : {total}")
    print(f"  Valid (OK)     : {flag_counts.get(FLAG_OK, 0)}")
    print(f"  Invalid        : {len(invalid)}")
    for flag, count in sorted(flag_counts.items()):
        if flag != FLAG_OK:
            print(f"    {flag:<28}: {count}")
    print(f"{'='*60}\n")

    if invalid:
        print("  Issues found:")
        for r in invalid:
            print(f"  [{r['flag_type']}] Ward {r['ward_id']} | {r['category']} | {r['fiscal_year']}")
            print(f"    → {r['reason']}")
            if r["expected_amount"] is not None:
                print(f"    → Expected: ₹{r['expected_amount']:,.0f}  |  Reported: ₹{float(r['reported_amount'] or 0):,.0f}")
        print()

    # ── Write growth_output.csv (SKILL-05) ────────────────────────────────
    all_rows_raw = []
    with open(BUDGET_CSV, newline="", encoding="utf-8") as f:
        all_rows_raw = list(csv.DictReader(f))

    growth_rows = generate_growth_output(all_rows_raw)
    growth_fieldnames = [
        "ward_id", "category", "fiscal_year",
        "allocated_amount", "prev_year_allocated",
        "growth_pct", "growth_flag",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=growth_fieldnames)
        writer.writeheader()
        writer.writerows(growth_rows)

    print(f"[BudgetGuard] Growth output written to: {OUTPUT_CSV}")
    print(f"[BudgetGuard] Done. {len(growth_rows)} growth rows generated.")


if __name__ == "__main__":
    main()
