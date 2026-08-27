"""
UC-0C — Budget Growth Calculator
"""
import argparse
import csv
import sys

VALID_GROWTH_TYPES = ("MoM", "YoY")


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    required = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}
    if not required.issubset(reader.fieldnames or []):
        missing = required - set(reader.fieldnames or [])
        raise ValueError(f"Missing required columns: {missing}")

    null_rows = [r for r in rows if not r.get("actual_spend", "").strip()]
    if null_rows:
        print(f"WARNING: {len(null_rows)} row(s) have null actual_spend:")
        for nr in null_rows:
            note = nr.get("notes", "").strip() or "No reason provided"
            print(f"  {nr['period']} | {nr['ward']} | {nr['category']} | {note}")

    return rows, null_rows


def compute_growth(
    rows: list[dict], growth_type: str, ward: str, category: str
) -> list[dict]:
    sorted_rows = sorted(rows, key=lambda r: r["period"])
    results = []
    prev_actual = None

    for r in sorted_rows:
        period = r["period"]
        actual_str = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()

        if not actual_str:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "",
                "prev_period_actual": prev_actual if prev_actual is not None else "",
                "growth_rate": "N/A",
                "formula": "Not computed — null actual_spend",
                "flag": notes if notes else "No reason provided",
            })
            prev_actual = None
            continue

        actual = float(actual_str)

        if prev_actual is None:
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "prev_period_actual": "",
                "growth_rate": "N/A",
                "formula": "No previous period for comparison",
                "flag": "N/A - first period",
            })
        else:
            if growth_type == "MoM":
                growth = (actual - prev_actual) / prev_actual
            elif growth_type == "YoY":
                growth = (actual - prev_actual) / prev_actual

            growth_pct = round(growth * 100, 1)
            sign = "+" if growth_pct >= 0 else ""
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": actual,
                "prev_period_actual": prev_actual,
                "growth_rate": f"{sign}{growth_pct}%",
                "formula": f"({actual} - {prev_actual}) / {prev_actual} * 100",
                "flag": "",
            })

        prev_actual = actual

    return results


def main(input_path: str, ward: str | None, category: str | None,
         growth_type: str, output_path: str):
    rows, null_rows = load_dataset(input_path)

    # Filter by ward and/or category
    if ward:
        rows = [r for r in rows if r["ward"] == ward]
    if category:
        rows = [r for r in rows if r["category"] == category]

    # Group by (ward, category)
    groups: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = (r["ward"], r["category"])
        groups.setdefault(key, []).append(r)

    all_results = []
    for (w, c), g_rows in sorted(groups.items()):
        all_results.extend(compute_growth(g_rows, growth_type, w, c))

    fieldnames = [
        "period", "ward", "category", "actual_spend",
        "prev_period_actual", "growth_rate", "formula", "flag",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"Done. {len(all_results)} rows written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help="Ward to filter (optional)")
    parser.add_argument("--category", help="Category to filter (optional)")
    parser.add_argument("--growth-type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    if not args.growth_type:
        print("ERROR: --growth-type is required. Must be 'MoM' or 'YoY'.", file=sys.stderr)
        sys.exit(1)
    if args.growth_type not in VALID_GROWTH_TYPES:
        print(f"ERROR: --growth-type must be one of {VALID_GROWTH_TYPES}. Got '{args.growth_type}'.", file=sys.stderr)
        sys.exit(1)

    main(args.input, args.ward, args.category, args.growth_type, args.output)
