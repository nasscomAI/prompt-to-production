"""
UC-0C — Budget Growth Calculator
Builds on the agent/skill definitions in agents.md and skills.md.
"""
import argparse
import csv
import sys

REQUIRED_COLS = {"period", "ward", "category", "budgeted_amount",
                 "actual_spend", "notes"}
VALID_GROWTH_TYPES = {"MoM"}


def load_dataset(path: str) -> tuple:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"Empty or invalid CSV: {path}")
        missing = REQUIRED_COLS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )
        rows = []
        null_rows = []
        for i, row in enumerate(reader, start=2):
            period = row.get("period", "").strip()
            ward = row.get("ward", "").strip()
            category = row.get("category", "").strip()
            actual = row.get("actual_spend", "").strip()
            notes = row.get("notes", "").strip()
            if not actual:
                null_rows.append({
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "notes": notes or "No reason provided",
                })
            rows.append(row)

    print(f"Loaded {len(rows)} rows. {len(null_rows)} null actual_spend rows "
          f"detected.", file=sys.stderr)
    for nr in null_rows:
        print(f"  NULL: {nr['period']} | {nr['ward']} | {nr['category']} "
              f"| {nr['notes']}", file=sys.stderr)

    return rows, null_rows


def compute_growth(rows: list, ward: str, category: str,
                   growth_type: str) -> list:
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            f"Supported: {', '.join(sorted(VALID_GROWTH_TYPES))}"
        )

    filtered = [r for r in rows
                if r["ward"].strip() == ward
                and r["category"].strip() == category]
    filtered.sort(key=lambda r: r["period"])

    if not filtered:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'"
        )

    formula = "((current_actual - previous_actual) / previous_actual) * 100"
    output = []
    previous_actual = None

    for row in filtered:
        period = row["period"].strip()
        actual_raw = row.get("actual_spend", "").strip()
        notes = row.get("notes", "").strip()

        if not actual_raw:
            output.append({
                "period": period,
                "actual_spend": "NULL",
                "previous_spend": "",
                "growth_pct": "N/A",
                "formula": "",
                "null_flag": notes or "No reason provided",
            })
            previous_actual = None
            continue

        current = float(actual_raw)
        entry = {
            "period": period,
            "actual_spend": str(current),
            "previous_spend": str(previous_actual) if previous_actual is not None else "",
            "growth_pct": "",
            "formula": "",
            "null_flag": "",
        }

        if previous_actual is not None and previous_actual != 0:
            growth = ((current - previous_actual) / previous_actual) * 100
            entry["growth_pct"] = f"{growth:+.1f}%"
            entry["formula"] = formula
        elif previous_actual is not None and previous_actual == 0:
            entry["growth_pct"] = "N/A (division by zero)"
            entry["formula"] = formula
        else:
            entry["growth_pct"] = "N/A (first period)"
            entry["formula"] = ""

        previous_actual = current
        output.append(entry)

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name to filter")
    parser.add_argument("--category", required=True,
                        help="Category to filter")
    parser.add_argument("--growth-type", required=True,
                        choices=["MoM"],
                        help="Growth calculation type (MoM only)")
    parser.add_argument("--output", required=True,
                        help="Path to write output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    out_fields = ["period", "actual_spend", "previous_spend",
                  "growth_pct", "formula", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output}")


if __name__ == "__main__":
    main()
