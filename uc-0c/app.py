"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        rows: list[dict] = []
        null_rows: list[dict] = []
        for row in reader:
            row_copy = dict(row)
            actual_raw = (row_copy.get("actual_spend") or "").strip()
            if actual_raw == "":
                row_copy["actual_spend"] = None
                null_rows.append(
                    {
                        "period": row_copy["period"],
                        "ward": row_copy["ward"],
                        "category": row_copy["category"],
                        "notes": row_copy.get("notes", ""),
                    }
                )
            else:
                row_copy["actual_spend"] = float(actual_raw)
            rows.append(row_copy)

    return rows, null_rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    if not growth_type:
        raise ValueError("growth-type is required. Please specify --growth-type explicitly.")
    if growth_type != "MoM":
        raise ValueError(f"Unsupported growth type: {growth_type}. Supported: MoM")

    target = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not target:
        raise ValueError("No rows found for requested ward/category.")

    target.sort(key=lambda r: r["period"])

    result: list[dict] = []
    prev_actual = None
    for row in target:
        period = row["period"]
        actual = row["actual_spend"]
        notes = row.get("notes", "") or ""
        formula = "(current_actual - previous_actual) / previous_actual * 100"

        if actual is None:
            result.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_type": growth_type,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "NULL_FLAGGED",
                    "null_reason": notes,
                }
            )
            prev_actual = None
            continue

        if prev_actual is None:
            result.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual:.1f}",
                    "growth_type": growth_type,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "BASE_PERIOD",
                    "null_reason": "",
                }
            )
            prev_actual = actual
            continue

        if prev_actual == 0:
            result.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{actual:.1f}",
                    "growth_type": growth_type,
                    "formula": formula,
                    "growth_percent": "",
                    "status": "DENOMINATOR_ZERO",
                    "null_reason": "Previous period actual_spend is zero",
                }
            )
            prev_actual = actual
            continue

        growth = ((actual - prev_actual) / prev_actual) * 100.0
        result.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": f"{actual:.1f}",
                "growth_type": growth_type,
                "formula": formula,
                "growth_percent": f"{growth:.1f}",
                "status": "OK",
                "null_reason": "",
            }
        )
        prev_actual = actual

    return result


def main():
    parser = argparse.ArgumentParser(description="UC-0C Number That Looks Right")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name")
    parser.add_argument("--category", required=True, help="Category name")
    parser.add_argument("--growth-type", required=True, help="Growth type (MoM)")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    if null_rows:
        print(f"Null actual_spend rows found: {len(null_rows)}")
        for r in null_rows:
            print(
                f"- {r['period']} | {r['ward']} | {r['category']} | reason: {r.get('notes', '')}"
            )

    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    out_fields = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "null_reason",
    ]
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(growth_rows)

    print(f"Done. Wrote {len(growth_rows)} rows to {args.output}")

if __name__ == "__main__":
    main()
