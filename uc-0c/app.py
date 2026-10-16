#!/usr/bin/env python3
"""
UC-0C: Budget Growth Calculator
No external dependencies — uses only Python built-ins.
"""

import argparse
import sys
import os
import csv


# ─── Skills ───────────────────────────────────────────────────────────────────

def load_dataset(path: str) -> list[dict]:
    """
    Skill: load_dataset
    Reads CSV, validates columns, reports null count and which rows before returning.
    """
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("[ERROR] File is empty.", file=sys.stderr)
        sys.exit(1)

    missing = required_cols - set(rows[0].keys())
    if missing:
        print(f"[ERROR] Missing required columns: {missing}", file=sys.stderr)
        sys.exit(1)

    # Report nulls BEFORE any computation
    null_rows = [r for r in rows if r["actual_spend"].strip() == ""]
    print(f"[INFO] Dataset loaded: {len(rows)} rows")
    print(f"[INFO] Null actual_spend rows detected: {len(null_rows)}")

    if null_rows:
        print("\n[NULL REPORT] The following rows have missing actual_spend values:")
        for r in null_rows:
            reason = r["notes"].strip() or "No reason provided"
            print(f"  • {r['period']} | {r['ward']} | {r['category']}")
            print(f"    Reason: {reason}")
        print()

    return rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """
    Skill: compute_growth
    Filters to ward + category, computes per-period growth with formula shown.
    """
    subset = [r for r in rows if r["ward"] == ward and r["category"] == category]
    subset.sort(key=lambda r: r["period"])

    if not subset:
        print(f"[ERROR] No data found for ward='{ward}', category='{category}'", file=sys.stderr)
        sys.exit(1)

    results = []

    for i, row in enumerate(subset):
        period = row["period"]
        raw = row["actual_spend"].strip()
        note = row["notes"].strip()

        if raw == "":
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend_lakh": "NULL",
                "growth": "NOT COMPUTED — null actual_spend",
                "formula": "N/A",
                "null_reason": note,
            })
            continue

        actual = float(raw)

        if growth_type == "MoM":
            if i == 0:
                growth_str = "N/A (first period)"
                formula_str = "N/A (no prior month)"
            else:
                prev_raw = subset[i - 1]["actual_spend"].strip()

                if prev_raw == "":
                    growth_str = "NOT COMPUTED — prior month is null"
                    formula_str = f"({actual} − NULL) / NULL × 100  →  undefined"
                else:
                    prev = float(prev_raw)
                    if prev == 0:
                        growth_str = "NOT COMPUTED — prior month spend is zero (division by zero)"
                        formula_str = f"({actual} − 0) / 0 × 100  →  undefined"
                    else:
                        pct = (actual - prev) / prev * 100
                        sign = "+" if pct >= 0 else ""
                        growth_str = f"{sign}{pct:.1f}%"
                        formula_str = f"({actual} − {prev}) / {prev} × 100 = {sign}{pct:.1f}%"

        elif growth_type == "YoY":
            growth_str = "NOT COMPUTED — YoY requires prior year data (only 2024 available)"
            formula_str = "N/A (insufficient year range)"

        else:
            print(f"[ERROR] Unknown growth_type '{growth_type}'. Use MoM or YoY.", file=sys.stderr)
            sys.exit(1)

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend_lakh": actual,
            "growth": growth_str,
            "formula": formula_str,
            "null_reason": "",
        })

    return results


# ─── Agent Rules ──────────────────────────────────────────────────────────────

def validate_args(args):
    if not args.growth_type:
        print("[REFUSED] --growth-type was not specified.", file=sys.stderr)
        print("  Please provide --growth-type MoM or --growth-type YoY.", file=sys.stderr)
        print("  The system will not guess the growth type.", file=sys.stderr)
        sys.exit(1)

    if not args.ward:
        print("[REFUSED] --ward was not specified.", file=sys.stderr)
        print("  Aggregating across all wards is not permitted.", file=sys.stderr)
        sys.exit(1)

    if not args.category:
        print("[REFUSED] --category was not specified.", file=sys.stderr)
        print("  Aggregating across all categories is not permitted.", file=sys.stderr)
        sys.exit(1)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward")
    parser.add_argument("--category")
    parser.add_argument("--growth-type", dest="growth_type")
    parser.add_argument("--output", default="growth_output.csv")
    args = parser.parse_args()

    validate_args(args)

    rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.output)
    fieldnames = ["period", "ward", "category", "actual_spend_lakh", "growth", "formula", "null_reason"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"[OUTPUT] Written to: {out_path}")
    print()
    col_widths = {k: max(len(k), max(len(str(r[k])) for r in results)) for k in fieldnames}
    header = "  ".join(k.ljust(col_widths[k]) for k in fieldnames)
    print(header)
    print("-" * len(header))
    for r in results:
        print("  ".join(str(r[k]).ljust(col_widths[k]) for k in fieldnames))


if __name__ == "__main__":
    main()