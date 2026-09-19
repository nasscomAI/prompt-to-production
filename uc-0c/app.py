"""UC-0C scoped month-over-month budget growth calculator."""
import argparse
import csv
from pathlib import Path

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

def load_dataset(input_path):
    with open(input_path, newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        rows = list(reader)
    nulls = [row for row in rows if not str(row["actual_spend"]).strip()]
    return rows, nulls

def compute_growth(rows, ward, category, growth_type):
    if not ward or ward.strip().lower() in {"all", "all wards"} or not category or category.strip().lower() in {"all", "all categories"}:
        raise ValueError("A single ward and category are required; all-ward aggregation is refused")
    if growth_type != "MoM":
        raise ValueError("growth_type must be explicitly set to MoM")
    selected = sorted((r for r in rows if r["ward"] == ward and r["category"] == category), key=lambda r: r["period"])
    if not selected:
        raise ValueError("No rows found for the requested ward/category")
    output = []
    previous = None
    for row in selected:
        current_text = row["actual_spend"].strip()
        current = float(current_text) if current_text else None
        formula = "BASELINE — no prior month"
        growth = ""
        status = "BASELINE" if previous is None and current is not None else "OK"
        note = row.get("notes", "")
        if current is None:
            status = "FLAGGED_NULL"
            formula = f"NOT COMPUTED — actual_spend is NULL; reason: {note or 'no reason supplied'}"
        elif previous is None:
            if output:
                status = "FLAGGED_PRIOR_NULL"
                formula = f"NOT COMPUTED — prior month actual_spend is NULL; current={current:.1f}"
            else:
                status = "BASELINE"
        else:
            growth_value = (current - previous) / previous * 100 if previous != 0 else None
            if growth_value is None:
                status = "FLAGGED_ZERO_BASE"
                formula = f"NOT COMPUTED — prior month actual_spend={previous:.1f} makes the denominator zero"
            else:
                growth = f"{growth_value:+.1f}%"
                formula = f"({current:.1f} - {previous:.1f}) / {previous:.1f} × 100"
        output.append({"period": row["period"], "ward": ward, "category": category, "actual_spend": current_text, "growth_type": growth_type, "growth_pct": growth, "status": status, "formula": formula, "notes": note})
        previous = current
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows, _ = load_dataset(args.input)
    result = compute_growth(rows, args.ward, args.category, args.growth_type)
    with open(args.output, "w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    print(f"Done. Wrote {len(result)} per-period rows to {args.output}")

if __name__ == "__main__":
    main()
