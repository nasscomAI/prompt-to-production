import argparse
import csv
import sys

REQUIRED_COLS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(filepath):
    rows = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Empty CSV — no columns found")
        missing = REQUIRED_COLS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for r in reader:
            rows.append(r)

    null_rows = [r for r in rows if r["actual_spend"].strip() == ""]
    print(f"Loaded {len(rows)} rows from {filepath}")
    print(f"Null actual_spend count: {len(null_rows)}")
    if null_rows:
        print("Null rows (period | ward | category | notes):")
        for r in null_rows:
            print(f"  {r['period']} | {r['ward']} | {r['category']} | {r['notes']}")

    return rows


def compute_growth(rows, ward, category, growth_type):
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        print(f"No data found for ward '{ward}' and category '{category}'")
        return []

    filtered.sort(key=lambda r: r["period"])

    out = []
    for i, r in enumerate(filtered):
        actual_raw = r["actual_spend"].strip()
        prev_actual_raw = filtered[i - 1]["actual_spend"].strip() if i > 0 else ""

        if actual_raw == "":
            growth = "NULL — not computed"
            formula = f"actual_spend is NULL: {r['notes']}"
        elif growth_type == "MoM":
            if i == 0:
                growth = "N/A (first period)"
                formula = "No previous period for MoM comparison"
            elif prev_actual_raw == "":
                growth = "NULL — not computed"
                formula = f"Previous period actual_spend is NULL"
            else:
                prev_val = float(prev_actual_raw)
                curr_val = float(actual_raw)
                if prev_val == 0:
                    growth = "N/A (division by zero)"
                    formula = "Previous actual_spend is 0, cannot compute"
                else:
                    pct = ((curr_val - prev_val) / prev_val) * 100
                    growth = f"{pct:+.1f}%"
                    formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100 = {pct:+.1f}%"
        elif growth_type == "YoY":
            prev_year = str(int(r["period"][:4]) - 1) + r["period"][4:]
            prev_rows = [x for x in filtered if x["period"] == prev_year and x["ward"] == ward and x["category"] == category]
            if not prev_rows:
                growth = "N/A (no prior year data)"
                formula = f"No data for period {prev_year}"
            else:
                prev_val = float(prev_rows[0]["actual_spend"])
                curr_val = float(actual_raw)
                if prev_val == 0:
                    growth = "N/A (division by zero)"
                    formula = "Prior year actual_spend is 0, cannot compute"
                else:
                    pct = ((curr_val - prev_val) / prev_val) * 100
                    growth = f"{pct:+.1f}%"
                    formula = f"(({curr_val} - {prev_val}) / {prev_val}) * 100 = {pct:+.1f}%"
        else:
            raise ValueError(f"Unsupported growth_type: {growth_type}")

        out.append({
            "period": r["period"],
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": r["actual_spend"] if actual_raw != "" else "NULL",
            "growth": growth,
            "formula": formula,
            "notes": r["notes"] if r["notes"].strip() else "",
        })

    return out


def main():
    parser = argparse.ArgumentParser(description="Compute ward budget growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True, help="Category to filter")
    parser.add_argument("--growth-type", choices=["MoM", "YoY"], help="Growth type")
    parser.add_argument("--output", required=True, help="Output CSV path")
    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type is required. Must be 'MoM' or 'YoY'. Refusing to guess.")
        sys.exit(1)

    rows = load_dataset(args.input)

    result = compute_growth(rows, args.ward, args.category, args.growth_type)

    if not result:
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth", "formula", "notes"]
    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"\nWrote {len(result)} rows to {args.output}")
    print(f"Ward: {args.ward}")
    print(f"Category: {args.category}")
    print(f"Growth type: {args.growth_type}")


if __name__ == "__main__":
    main()
