"""
UC-0C growth analysis CLI.
Implements AGENTS.md and skills.md constraints for per-ward/per-category growth.
"""
import argparse
import csv
import os
from typing import Dict, List, Optional


REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]
SUPPORTED_GROWTH_TYPES = {"MOM", "YOY"}
AGGREGATION_TOKENS = {"ANY", "ALL", "*", "CITY", "CITYWIDE", "CITY-WIDE"}


def normalize_growth_type(growth_type: Optional[str]) -> str:
    if not growth_type:
        raise ValueError("Refusal: --growth-type is required (choose MoM or YoY).")
    normalized = growth_type.strip().upper()
    if normalized not in SUPPORTED_GROWTH_TYPES:
        raise ValueError(
            f"Refusal: unsupported --growth-type '{growth_type}'. Use MoM or YoY."
        )
    return normalized


def guard_single_dimension(value: Optional[str], field_name: str) -> str:
    if value is None or not value.strip():
        raise ValueError(f"Refusal: --{field_name} is required; aggregation is not allowed.")
    normalized = value.strip()
    if normalized.upper() in AGGREGATION_TOKENS:
        raise ValueError(
            f"Refusal: --{field_name}='{value}' implies aggregation. "
            "Provide one explicit ward and one explicit category."
        )
    return normalized


def parse_float(raw: str) -> Optional[float]:
    if raw is None:
        return None
    cleaned = raw.strip()
    if cleaned == "":
        return None
    return float(cleaned)


def load_dataset(input_path: str) -> Dict[str, object]:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV parse error: no header row found.")

        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV schema error: missing required columns {missing}")

        rows: List[Dict[str, object]] = []
        null_rows: List[Dict[str, str]] = []
        wards = set()
        categories = set()

        for row in reader:
            parsed = {
                "period": row["period"].strip(),
                "ward": row["ward"].strip(),
                "category": row["category"].strip(),
                "budgeted_amount": parse_float(row["budgeted_amount"]),
                "actual_spend": parse_float(row["actual_spend"]),
                "notes": (row.get("notes") or "").strip(),
            }
            rows.append(parsed)
            wards.add(parsed["ward"])
            categories.add(parsed["category"])
            if parsed["actual_spend"] is None:
                null_rows.append(
                    {
                        "period": parsed["period"],
                        "ward": parsed["ward"],
                        "category": parsed["category"],
                        "notes": parsed["notes"],
                    }
                )

    return {
        "rows": rows,
        "null_count": len(null_rows),
        "null_rows": null_rows,
        "wards": sorted(wards),
        "categories": sorted(categories),
    }


def compute_growth(
    rows: List[Dict[str, object]], ward: str, category: str, growth_type: str
) -> List[Dict[str, object]]:
    filtered = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise ValueError(
            f"No data found for ward='{ward}' and category='{category}'."
        )

    filtered.sort(key=lambda r: str(r["period"]))
    output: List[Dict[str, object]] = []

    for i, row in enumerate(filtered):
        curr = row["actual_spend"]
        period = str(row["period"])
        formula = ""
        growth_pct = None
        status = "computed"
        null_reason = ""

        if curr is None:
            status = "null_actual_spend"
            null_reason = str(row["notes"] or "actual_spend is null")
            formula = "N/A (current actual_spend is null)"
        else:
            if growth_type == "MOM":
                if i == 0:
                    status = "insufficient_history"
                    formula = "N/A (first month has no previous month)"
                else:
                    prev = filtered[i - 1]["actual_spend"]
                    if prev is None:
                        status = "previous_null"
                        formula = "N/A (previous month actual_spend is null)"
                    elif prev == 0:
                        status = "division_by_zero"
                        formula = "N/A (previous month actual_spend is 0)"
                    else:
                        growth_pct = ((float(curr) - float(prev)) / float(prev)) * 100.0
                        formula = f"(({curr:.2f} - {prev:.2f}) / {prev:.2f}) * 100"
            else:  # YOY
                if i < 12:
                    status = "insufficient_history"
                    formula = "N/A (YoY requires same month previous year)"
                else:
                    prev = filtered[i - 12]["actual_spend"]
                    if prev is None:
                        status = "previous_null"
                        formula = "N/A (same month previous year actual_spend is null)"
                    elif prev == 0:
                        status = "division_by_zero"
                        formula = "N/A (same month previous year actual_spend is 0)"
                    else:
                        growth_pct = ((float(curr) - float(prev)) / float(prev)) * 100.0
                        formula = f"(({curr:.2f} - {prev:.2f}) / {prev:.2f}) * 100"

        output.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": "" if curr is None else f"{float(curr):.2f}",
                "growth_type": growth_type,
                "formula": formula,
                "growth_pct": "" if growth_pct is None else f"{growth_pct:.2f}",
                "status": status,
                "null_reason": null_reason,
            }
        )

    return output


def write_output(output_path: str, rows: List[Dict[str, object]]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_pct",
        "status",
        "null_reason",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C budget growth calculator")
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--ward", help="Single ward name (required)")
    parser.add_argument("--category", help="Single category name (required)")
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    growth_type = normalize_growth_type(args.growth_type)
    ward = guard_single_dimension(args.ward, "ward")
    category = guard_single_dimension(args.category, "category")

    dataset = load_dataset(args.input)
    null_rows = dataset["null_rows"]
    print(f"Detected null actual_spend rows: {dataset['null_count']}")
    for null_row in null_rows:
        print(
            "- {period} | {ward} | {category} | reason: {notes}".format(**null_row)
        )

    computed_rows = compute_growth(
        dataset["rows"], ward=ward, category=category, growth_type=growth_type
    )
    write_output(args.output, computed_rows)
    print(
        f"Wrote {len(computed_rows)} rows for ward='{ward}', "
        f"category='{category}', growth_type='{growth_type}' to {args.output}"
    )


if __name__ == "__main__":
    main()
