"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from typing import Dict, List, Tuple

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    with open(input_path, "r", newline="", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

        rows = list(reader)

    null_rows = []
    for row in rows:
        if (row.get("actual_spend") or "").strip() == "":
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "null_reason": (row.get("notes") or "").strip(),
                }
            )
    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, str]], ward: str, category: str, growth_type: str
) -> List[Dict[str, str]]:
    if not growth_type:
        raise ValueError("growth_type is required. Use MoM or YoY.")

    growth_type = growth_type.upper()
    if growth_type not in {"MOM", "YOY"}:
        raise ValueError("Invalid growth_type. Use MoM or YoY.")

    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise ValueError("No rows found for the specified ward and category.")

    filtered.sort(key=lambda r: r["period"])
    out_rows: List[Dict[str, str]] = []

    for i, row in enumerate(filtered):
        current_raw = (row.get("actual_spend") or "").strip()
        is_null = current_raw == ""
        current_val = float(current_raw) if not is_null else None

        result = {
            "period": row["period"],
            "ward": ward,
            "category": category,
            "budgeted_amount": row["budgeted_amount"],
            "actual_spend": current_raw if current_raw else "NULL",
            "is_null": "YES" if is_null else "NO",
            "null_reason": (row.get("notes") or "").strip(),
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": "NA",
            "status": "",
        }

        if is_null:
            result["status"] = "NULL_ACTUAL_SPEND_FLAGGED"
            result["formula"] = "NA (current actual_spend is NULL)"
            out_rows.append(result)
            continue

        back = 1 if growth_type == "MOM" else 12
        if i - back < 0:
            result["status"] = "BASE_PERIOD_NO_PREVIOUS"
            result["formula"] = (
                "NA (no previous month)"
                if growth_type == "MOM"
                else "NA (no previous year period)"
            )
            out_rows.append(result)
            continue

        prev_row = filtered[i - back]
        prev_raw = (prev_row.get("actual_spend") or "").strip()
        if prev_raw == "":
            result["status"] = "PREVIOUS_PERIOD_NULL"
            result["formula"] = "NA (previous period actual_spend is NULL)"
            out_rows.append(result)
            continue

        prev_val = float(prev_raw)
        if prev_val == 0:
            result["status"] = "PREVIOUS_PERIOD_ZERO"
            result["formula"] = "NA (previous period actual_spend is 0)"
            out_rows.append(result)
            continue

        growth = ((current_val - prev_val) / prev_val) * 100
        result["formula"] = f"(({current_val:.1f} - {prev_val:.1f}) / {prev_val:.1f}) * 100"
        result["growth_percent"] = f"{growth:.1f}%"
        result["status"] = "COMPUTED"
        out_rows.append(result)

    return out_rows


def write_output(output_path: str, out_rows: List[Dict[str, str]]):
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "is_null",
        "null_reason",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to growth output csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    # Make null scanning explicit before computation, as required by UC-0C.
    print(f"Detected null actual_spend rows: {len(null_rows)}")
    out_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, out_rows)
    print(f"Done. Growth output written to {args.output}")

if __name__ == "__main__":
    main()
