"""
UC-0C: Number That Looks Right
Ward budget auditor — detects silent aggregation errors in budget CSV.
Uses only Python standard library (no external dependencies).

Output: growth_output.csv
"""

import csv
import os
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE  = os.path.join(BASE_DIR, "..", "data", "budget", "ward_budget.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "growth_output.csv")
TOLERANCE   = 0.01   # floating-point mismatch threshold

# ── Load CSV ──────────────────────────────────────────────────────────────────
def load_budget(path: str) -> list:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

# ── Scoped aggregation — strictly per (ward, category) ───────────────────────
def compute_totals(rows: list) -> dict:
    """Sum `amount` grouped by (ward, category) only."""
    sums = defaultdict(float)
    for row in rows:
        key = (row["ward"].strip(), row["category"].strip())
        sums[key] += float(row["amount"])
    return sums

# ── Collect recorded totals per (ward, category) ─────────────────────────────
def collect_recorded(rows: list) -> dict:
    """
    The CSV may have one `total` value per (ward, category) group.
    We take the last recorded value for each group (they should all be identical
    within a group if the source data is well-formed).
    """
    recorded = {}
    for row in rows:
        key = (row["ward"].strip(), row["category"].strip())
        if "total" in row and row["total"].strip():
            recorded[key] = float(row["total"])
    return recorded

# ── Audit ─────────────────────────────────────────────────────────────────────
def audit(computed: dict, recorded: dict) -> list:
    results = []
    for key in sorted(computed.keys()):
        ward, category = key
        comp_val = computed[key]
        rec_val  = recorded.get(key, None)

        if rec_val is None:
            status = "NO_RECORDED_TOTAL"
        elif abs(comp_val - rec_val) <= TOLERANCE:
            status = "OK"
        else:
            status = "MISMATCH"

        results.append({
            "ward":           ward,
            "category":       category,
            "computed_total": round(comp_val, 2),
            "recorded_total": round(rec_val, 2) if rec_val is not None else "N/A",
            "status":         status,
        })
    return results

# ── Write output ──────────────────────────────────────────────────────────────
def write_output(results: list, path: str):
    fieldnames = ["ward", "category", "computed_total", "recorded_total", "status"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  UC-0C: Number That Looks Right — Budget Auditor")
    print("=" * 60)

    # Load
    if not os.path.exists(INPUT_FILE):
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        print("  Expected at: data/budget/ward_budget.csv")
        return

    rows = load_budget(INPUT_FILE)
    print(f"Loaded {len(rows)} row(s) from ward_budget.csv\n")

    # Compute
    computed = compute_totals(rows)
    recorded = collect_recorded(rows)

    # Audit
    results = audit(computed, recorded)

    # Print report to terminal
    ok_count       = sum(1 for r in results if r["status"] == "OK")
    mismatch_count = sum(1 for r in results if r["status"] == "MISMATCH")
    missing_count  = sum(1 for r in results if r["status"] == "NO_RECORDED_TOTAL")

    print(f"{'Ward':<20} {'Category':<25} {'Computed':>12} {'Recorded':>12}  Status")
    print("-" * 80)
    for r in results:
        print(
            f"{r['ward']:<20} {r['category']:<25} "
            f"{str(r['computed_total']):>12} {str(r['recorded_total']):>12}  {r['status']}"
        )

    print("-" * 80)
    print(f"\nSummary: {ok_count} OK  |  {mismatch_count} MISMATCH  |  {missing_count} NO_RECORDED_TOTAL")

    # Write CSV
    write_output(results, OUTPUT_FILE)
    print(f"\nOutput written to: growth_output.csv")
    print("Done ✓")

if __name__ == "__main__":
    main()
