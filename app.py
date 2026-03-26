"""
UC-0C: Number That Looks Right
BudgetAnalysisAgent — computes year-on-year ward+category budget growth
Output: growth_output.csv

CRAFT Loop applied:
  C — Critique: silent aggregation across wards/categories
  R — Refine: strict groupby(['ward','category'])
  A — Assert: self-check before export
  F — Fix: guard division by zero, missing prior year
  T — Test: sample row validation
"""

import csv
import json
import os
import sys


# ── Skill 1: Load and validate ──────────────────────────────────────────────

def load_budget_data(filepath):
    """Load ward_budget.csv and return list of dicts."""
    if not os.path.exists(filepath):
        print(f"[ERROR] File not found: {filepath}")
        sys.exit(1)

    rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [h.strip().lower() for h in reader.fieldnames]
        required = {"ward", "category", "year", "amount"}
        if not required.issubset(set(headers)):
            print(f"[ERROR] Missing columns. Found: {headers}")
            sys.exit(1)

        for row in reader:
            try:
                rows.append({
                    "ward":     row["ward"].strip(),
                    "category": row["category"].strip(),
                    "year":     int(row["year"].strip()),
                    "amount":   float(row["amount"].strip()),
                })
            except (ValueError, KeyError) as e:
                print(f"[WARN] Skipping bad row {row}: {e}")

    print(f"[INFO] Loaded {len(rows)} rows from {filepath}")
    return rows


# ── Skill 2: Compute growth per ward per category ───────────────────────────

def compute_growth(rows):
    """
    For each (ward, category) group, sort by year and compute
    year-on-year change and growth %.
    NEVER aggregates across wards or categories.
    """
    # Group strictly by (ward, category)
    groups = {}
    for row in rows:
        key = (row["ward"], row["category"])
        groups.setdefault(key, []).append(row)

    results = []
    for (ward, category), entries in groups.items():
        # Sort by year ascending within the group
        entries_sorted = sorted(entries, key=lambda x: x["year"])

        for i, entry in enumerate(entries_sorted):
            current_year   = entry["year"]
            current_amount = entry["amount"]

            if i == 0:
                # No previous year in dataset
                prev_year   = "N/A"
                prev_amount = "N/A"
                change      = "N/A"
                growth_pct  = "N/A"
                trend       = "N/A"
            else:
                prev        = entries_sorted[i - 1]
                prev_year   = prev["year"]
                prev_amount = prev["amount"]

                change = current_amount - prev_amount

                if prev_amount == 0:
                    growth_pct = "N/A"
                else:
                    growth_pct = round((change / prev_amount) * 100, 2)

                if change > 0:
                    trend = "GROWTH"
                elif change < 0:
                    trend = "DECLINE"
                else:
                    trend = "NO_CHANGE"

            results.append({
                "ward":           ward,
                "category":       category,
                "year":           current_year,
                "amount":         current_amount,
                "prev_year":      prev_year,
                "prev_amount":    prev_amount,
                "change":         change,
                "growth_pct":     growth_pct,
                "trend":          trend,
            })

    return results


# ── Skill 3: Flag anomalies ──────────────────────────────────────────────────

def flag_anomalies(results):
    for r in results:
        gp = r["growth_pct"]
        if gp == "N/A":
            r["anomaly_flag"] = "MISSING_PRIOR_YEAR"
        elif gp > 100:
            r["anomaly_flag"] = "HIGH_GROWTH"
        elif gp < -50:
            r["anomaly_flag"] = "HIGH_DECLINE"
        else:
            r["anomaly_flag"] = "OK"
    return results


# ── Skill 4: Export results ──────────────────────────────────────────────────

def export_results(results, output_path="growth_output.csv"):
    """Write sorted results to growth_output.csv."""
    # Sort: ward ASC, category ASC, year DESC
    def sort_key(r):
        return (r["ward"], r["category"], -r["year"])

    results_sorted = sorted(results, key=sort_key)

    fieldnames = [
        "ward", "category", "year", "amount",
        "prev_year", "prev_amount", "change",
        "growth_pct", "trend", "anomaly_flag"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_sorted)

    print(f"[INFO] Exported {len(results_sorted)} rows → {output_path}")
    return output_path


# ── Skill 5: Self-check (CRAFT enforcement) ──────────────────────────────────

def run_self_check(results):
    """Validate output before saving."""
    print("\n── Self-Check (CRAFT) ──")
    all_pass = True

    # Check 1: No row spans multiple wards
    for r in results:
        if "," in r["ward"] or "/" in r["ward"]:
            print(f"[FAIL] Multi-ward row detected: {r['ward']}")
            all_pass = False
            break
    else:
        print("[PASS] No multi-ward rows")

    # Check 2: No row spans multiple categories
    for r in results:
        if "," in r["category"] or "/" in r["category"]:
            print(f"[FAIL] Multi-category row detected: {r['category']}")
            all_pass = False
            break
    else:
        print("[PASS] No multi-category rows")

    # Check 3: growth_pct formula check on first calculable row
    calculable = [r for r in results if r["growth_pct"] != "N/A"]
    if calculable:
        sample = calculable[0]
        expected = round((sample["change"] / sample["prev_amount"]) * 100, 2)
        if sample["growth_pct"] == expected:
            print(f"[PASS] Growth formula correct on sample row")
        else:
            print(f"[FAIL] Formula mismatch: got {sample['growth_pct']}, expected {expected}")
            all_pass = False
    else:
        print("[SKIP] No calculable rows to verify formula")

    # Check 4: trend consistency
    trend_errors = 0
    for r in results:
        if r["growth_pct"] == "N/A":
            continue
        if r["growth_pct"] > 0 and r["trend"] != "GROWTH":
            trend_errors += 1
        if r["growth_pct"] < 0 and r["trend"] != "DECLINE":
            trend_errors += 1
        if r["growth_pct"] == 0 and r["trend"] != "NO_CHANGE":
            trend_errors += 1
    if trend_errors == 0:
        print("[PASS] Trend labels consistent with growth_pct")
    else:
        print(f"[FAIL] {trend_errors} trend label mismatches")
        all_pass = False

    print(f"── Self-Check Result: {'ALL PASS ✓' if all_pass else 'FAILURES DETECTED ✗'} ──\n")
    return all_pass


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Locate data file (handles running from repo root or uc-0c/)
    candidates = [
        "data/budget/ward_budget.csv",
        "../data/budget/ward_budget.csv",
    ]
    filepath = None
    for c in candidates:
        if os.path.exists(c):
            filepath = c
            break

    if filepath is None:
        print("[ERROR] Cannot find ward_budget.csv. Run from repo root.")
        sys.exit(1)

    print("=" * 50)
    print("UC-0C: Number That Looks Right — BudgetAnalysisAgent")
    print("=" * 50)

    # Skill 1: Load
    rows = load_budget_data(filepath)

    # Skill 2: Compute growth
    results = compute_growth(rows)

    # Skill 3: Flag anomalies
    results = flag_anomalies(results)

    # Skill 5: Self-check BEFORE export
    passed = run_self_check(results)
    if not passed:
        print("[ABORT] Self-check failed. Fix issues before exporting.")
        sys.exit(1)

    # Skill 4: Export
    out_path = export_results(results)

    print(f"\n[DONE] growth_output.csv ready at: {os.path.abspath(out_path)}")
    print("Submit this file along with your PR.\n")


if __name__ == "__main__":
    main()
