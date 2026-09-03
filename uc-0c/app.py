"""
UC-0C — Number That Looks Right | Vibe Coding Workshop (Civic Tech Edition)

Workshop workflow: RICE → agents.md → skills.md → CRAFT
Author: Sneha (participant/Sneha-Amritsar)

Enforcement:
  - Per-ward per-category only — refuse aggregation (exit 2).
  - Flag every null actual_spend before computing (notes copied).
  - Show formula every row: MoM: (cur-prev)/prev*100=+x.x% or NULL/N/A.
  - Refuse if --growth-type missing — never guess.

Skills: load_dataset, compute_growth, verification
Usage:
  python app.py --input data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REQUIRED_COLUMNS: List[str] = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES: List[str] = ["MoM", "YoY"]

KNOWN_NULLS: set[Tuple[str, str, str]] = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
}


def load_dataset(input_path: str) -> List[Dict[str, str]]:
    """Read CSV, validate columns, report nulls, return typed rows.

    Args:
        input_path: Path to ward_budget.csv.

    Returns:
        List of row dicts with added _actual (float|None) and _budgeted (float).

    Raises:
        FileNotFoundError: If file missing.
        ValueError: If header missing or required columns absent.
    """
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"Dataset not found: {input_path}")
    with open(p, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns: {missing} vs found {reader.fieldnames}")
        rows = list(reader)
        for r in rows:
            val = r.get("actual_spend", "").strip() if r.get("actual_spend") is not None else ""
            if val == "":
                r["_actual"] = None
            else:
                try:
                    r["_actual"] = float(val)
                except ValueError:
                    r["_actual"] = None
            try:
                r["_budgeted"] = float(r.get("budgeted_amount", "").strip() or 0)
            except ValueError:
                r["_budgeted"] = None

        null_rows = [r for r in rows if r["_actual"] is None]
        print(f"load_dataset: {len(rows)} rows, {len(null_rows)} null actual_spend", file=sys.stderr)
        if null_rows:
            for r in null_rows:
                print(f"  NULL: {r['period']} | {r['ward']} | {r['category']} | notes: {r.get('notes','')}", file=sys.stderr)
        return rows


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    """Compute per-period growth for single ward+category with formula.

    Args:
        rows: Full dataset from load_dataset.
        ward: Exact ward name (e.g., "Ward 1 – Kasba").
        category: Exact category (e.g., "Roads & Pothole Repair").
        growth_type: "MoM" or "YoY".

    Returns:
        List of 12 dicts sorted by period with growth_pct and formula.

    Exits:
        2 on REFUSAL (aggregation, missing growth_type, not found).
    """
    if not growth_type:
        print("REFUSAL: --growth-type required (MoM or YoY) — never guess formula.", file=sys.stderr)
        sys.exit(2)
    if growth_type not in GROWTH_TYPES:
        print(f"REFUSAL: Unsupported growth-type '{growth_type}'. Use MoM or YoY.", file=sys.stderr)
        sys.exit(2)
    if not ward or not category:
        print("REFUSAL: Aggregation across wards/categories not allowed — specify single --ward and single --category.", file=sys.stderr)
        wards = sorted(set(r["ward"] for r in rows))
        cats = sorted(set(r["category"] for r in rows))
        print(f"  Available wards: {wards}", file=sys.stderr)
        print(f"  Available categories: {cats}", file=sys.stderr)
        sys.exit(2)

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        print(f"REFUSAL: No rows for ward='{ward}' category='{category}'.", file=sys.stderr)
        wards = sorted(set(r["ward"] for r in rows))
        cats = sorted(set(r["category"] for r in rows))
        print(f"  Available wards: {wards}", file=sys.stderr)
        print(f"  Available categories: {cats}", file=sys.stderr)
        sys.exit(2)

    filtered.sort(key=lambda r: r["period"])
    output: List[Dict[str, str]] = []
    for i, r in enumerate(filtered):
        period = r["period"]
        actual = r["_actual"]
        notes = r.get("notes", "").strip()
        if actual is None:
            growth = ""
            formula = f"NULL: flagged — {notes if notes else 'actual_spend is null'}"
            flag_notes = f"FLAGGED NULL — {notes}" if notes else "FLAGGED NULL"
        else:
            if i == 0:
                growth = ""
                formula = "N/A: first period, no previous"
                flag_notes = notes
            else:
                prev = filtered[i - 1]
                prev_actual = prev["_actual"]
                if prev_actual is None or prev_actual == 0:
                    growth = ""
                    formula = f"N/A: previous period {prev['period']} is NULL ({prev.get('notes','')}) — cannot compute"
                    flag_notes = notes
                else:
                    if growth_type == "MoM":
                        val = (actual - prev_actual) / prev_actual * 100
                        growth = f"{val:+.1f}%"
                        formula = f"MoM: ({actual}-{prev_actual})/{prev_actual}*100={val:+.1f}%"
                    else:  # YoY
                        growth = ""
                        formula = "N/A: YoY requires prior year data"
                    flag_notes = notes

        output.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": r.get("budgeted_amount", ""),
                "actual_spend": r.get("actual_spend", ""),
                "growth_pct": growth,
                "formula": formula,
                "notes": flag_notes,
            }
        )
    return output


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth — per-ward per-category MoM with null-flagging and formula.",
        epilog='Example: python app.py --input data/budget/ward_budget.csv --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" --growth-type MoM --output growth_output.csv',
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help='Ward name e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=False, default=None, help='Category e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    if not args.growth_type:
        print("REFUSAL: --growth-type required (MoM or YoY) — never guess formula.", file=sys.stderr)
        sys.exit(2)

    rows = load_dataset(args.input)

    if not args.ward or not args.category:
        print("REFUSAL: Aggregation across wards/categories not allowed — specify single --ward and single --category.", file=sys.stderr)
        wards = sorted(set(r["ward"] for r in rows))
        cats = sorted(set(r["category"] for r in rows))
        print(f"  Available wards: {wards}", file=sys.stderr)
        print(f"  Available categories: {cats}", file=sys.stderr)
        sys.exit(2)

    result = compute_growth(rows, args.ward, args.category, args.growth_type)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_pct", "formula", "notes"]
    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for r in result:
            writer.writerow(r)
    print(f"Done. Growth table written to {args.output} — {len(result)} periods, ward='{args.ward}' category='{args.category}' growth-type={args.growth_type}")


if __name__ == "__main__":
    main()
