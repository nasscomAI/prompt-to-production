"""
UC-0C — Number That Looks Right
RICE + agents.md + skills.md + CRAFT workflow
Enforcement: per-ward per-category only, flag nulls, show formula, refuse if growth-type missing
"""
import argparse
import csv
import sys
from pathlib import Path
from collections import defaultdict

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_TYPES = ["MoM", "YoY"]

# Known null rows per README for verification
KNOWN_NULLS = {
    ("2024-03", "Ward 2 – Shivajinagar", "Drainage & Flooding"),
    ("2024-07", "Ward 4 – Warje", "Roads & Pothole Repair"),
    ("2024-11", "Ward 1 – Kasba", "Waste Management"),
    ("2024-08", "Ward 3 – Kothrud", "Parks & Greening"),
    ("2024-05", "Ward 5 – Hadapsar", "Streetlight Maintenance"),
}


def load_dataset(input_path: str):
    """Read CSV, validate columns, report nulls, return rows."""
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
        # Parse types
        for r in rows:
            # normalize actual_spend
            val = r.get("actual_spend", "").strip() if r.get("actual_spend") is not None else ""
            if val == "":
                r["_actual"] = None
            else:
                try:
                    r["_actual"] = float(val)
                except ValueError:
                    r["_actual"] = None
            # budgeted
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


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Filter to ward+category, sort by period, compute growth with formula."""
    if not growth_type:
        print("REFUSAL: --growth-type required (MoM or YoY) — never guess formula.", file=sys.stderr)
        sys.exit(2)
    if growth_type not in GROWTH_TYPES:
        print(f"REFUSAL: Unsupported growth-type '{growth_type}'. Use MoM or YoY.", file=sys.stderr)
        sys.exit(2)
    if not ward or not category:
        print("REFUSAL: Aggregation across wards/categories not allowed — specify single --ward and single --category.", file=sys.stderr)
        # Show available values to help user
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

    # Sort by period YYYY-MM lexicographically works
    filtered.sort(key=lambda r: r["period"])

    # Detect if user tried to request all wards/categories (should refuse) — already handled by requiring exact match

    output = []
    for i, r in enumerate(filtered):
        period = r["period"]
        actual = r["_actual"]
        budgeted = r["_budgeted"]
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
                    elif growth_type == "YoY":
                        # YoY not applicable for single year; show N/A
                        growth = ""
                        formula = "N/A: YoY requires prior year data"
                    flag_notes = notes

        output.append({
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": r.get("budgeted_amount", ""),
            "actual_spend": r.get("actual_spend", ""),
            "growth_pct": growth,
            "formula": formula,
            "notes": flag_notes,
        })
    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=False, default=None, help='Ward name e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", required=False, default=None, help='Category e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", required=False, default=None, dest="growth_type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforce refusals before loading
    if not args.growth_type:
        print("REFUSAL: --growth-type required (MoM or YoY) — never guess formula.", file=sys.stderr)
        sys.exit(2)

    rows = load_dataset(args.input)

    # Additional refusal: if ward/category missing, refuse (no aggregation)
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
