"""
UC-0C — Number That Looks Right
Budget growth calculator implementing the enforcement rules from agents.md
(per-ward per-category only, null flagged, formula shown, refuse missing
--growth-type) and the skills from skills.md: load_dataset + compute_growth.
"""
import argparse
import csv
import sys


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(input_path: str):
    """Read the CSV, validate columns, surface nulls, return rows as dicts."""
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is empty or missing a header row.")
        if not REQUIRED_COLUMNS.issubset(set(reader.fieldnames)):
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            raise ValueError(f"Input CSV missing required columns: {sorted(missing)}")
        rows = list(reader)

    null_rows = []
    for r in rows:
        spend = r.get("actual_spend", "").strip()
        if spend == "":
            null_rows.append(r)
            if not r.get("notes", "").strip():
                r["notes"] = "No reason provided"

    print(f"Dataset loaded: {len(rows)} rows")
    print(f"Null actual_spend rows: {len(null_rows)}")
    if null_rows:
        for nr in null_rows:
            print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} — {nr['notes']}")
    return rows


def compute_growth(rows, ward: str, category: str, growth_type: str):
    """Compute per-period growth for one ward+category."""
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError(f"No data found for ward={ward!r}, category={category!r}")

    ward_unique = set(r["ward"] for r in rows)
    cat_unique = set(r["category"] for r in rows)
    if len(ward_unique) > 1 and ward not in ward_unique:
        raise ValueError(
            f"--ward must match exactly. Available: {sorted(ward_unique)}")
    if len(cat_unique) > 1 and category not in cat_unique:
        raise ValueError(
            f"--category must match exactly. Available: {sorted(cat_unique)}")

    filtered = sorted(filtered, key=lambda r: r["period"])
    periods = []
    for r in filtered:
        periods.append(r)

    output_rows = []
    prev_spend = None
    prev_period = None

    for i, r in enumerate(periods):
        spend_str = r["actual_spend"].strip()
        period = r["period"]
        budget = r["budgeted_amount"].strip()
        notes = r.get("notes", "").strip()

        out = {
            "period": period,
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": budget,
            "actual_spend": "",
            "notes": notes,
            "growth_pct": "",
            "growth_formula": "",
            "flag": "",
        }

        if spend_str == "":
            out["actual_spend"] = "NULL"
            out["growth_pct"] = "N/A"
            out["growth_formula"] = "N/A"
            out["flag"] = f"NULL — {notes}"
            prev_spend = None
            prev_period = None
            output_rows.append(out)
            continue

        spend = float(spend_str)
        out["actual_spend"] = f"{spend:.1f}"

        if prev_spend is None:
            out["growth_pct"] = "N/A"
            out["growth_formula"] = f"{growth_type} = N/A (no prior period)"
            out["flag"] = ""
        else:
            current = spend
            previous = prev_spend
            if previous == 0:
                pct = "N/A"
                formula = f"{growth_type} = N/A (previous is 0)"
            else:
                raw = (current - previous) / previous
                pct = f"{raw:+.1%}"
                formula = f"{growth_type} = ({current:.1f} - {previous:.1f}) / {previous:.1f}"
            out["growth_pct"] = pct
            out["growth_formula"] = formula
            out["flag"] = ""

        prev_spend = spend
        prev_period = period
        output_rows.append(out)

    return output_rows


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Number That Looks Right — Budget Growth Calculator")
    parser.add_argument("--input", required=True,
                        help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True,
                        help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True,
                        help="Exact category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type",
                        choices=["MoM", "YoY"],
                        help="Growth type: MoM (month-over-month) or YoY. Refuses if not specified.")
    parser.add_argument("--output", required=True,
                        help="Path to write growth_output.csv")
    args = parser.parse_args()

    if args.growth_type is None:
        print("ERROR: --growth-type must be specified (MoM or YoY). "
              "Refusing to guess.", file=sys.stderr)
        sys.exit(1)

    rows = load_dataset(args.input)
    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "period", "ward", "category", "budgeted_amount", "actual_spend",
            "notes", "growth_pct", "growth_formula", "flag",
        ])
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Growth table written to {args.output} "
          f"({len(output_rows)} rows)")


if __name__ == "__main__":
    main()