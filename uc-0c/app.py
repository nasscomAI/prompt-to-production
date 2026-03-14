"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def _parse_float(value):
    text = str(value or "").strip()
    if not text:
        return None
    return float(text)


def _parse_period(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m")


def _previous_period(period: str, growth_type: str) -> str:
    dt = _parse_period(period)
    if growth_type == "MoM":
        if dt.month == 1:
            return f"{dt.year - 1}-12"
        return f"{dt.year}-{dt.month - 1:02d}"
    if growth_type == "YoY":
        return f"{dt.year - 1}-{dt.month:02d}"
    raise ValueError("Unsupported growth type")


def load_dataset(input_path: str) -> dict:
    """
    Read CSV, validate schema, and collect null diagnostics.
    """
    try:
        with open(input_path, mode="r", encoding="utf-8", newline="") as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames or []
            missing_columns = [col for col in REQUIRED_COLUMNS if col not in fieldnames]
            if missing_columns:
                raise ValueError("Missing required columns: " + ", ".join(missing_columns))

            rows = []
            null_rows = []
            wards = set()
            categories = set()

            for row in reader:
                normalized = {
                    "period": str(row.get("period", "")).strip(),
                    "ward": str(row.get("ward", "")).strip(),
                    "category": str(row.get("category", "")).strip(),
                    "budgeted_amount": _parse_float(row.get("budgeted_amount")),
                    "actual_spend": _parse_float(row.get("actual_spend")),
                    "notes": str(row.get("notes", "")).strip(),
                }
                rows.append(normalized)
                wards.add(normalized["ward"])
                categories.add(normalized["category"])

                if normalized["actual_spend"] is None:
                    null_rows.append(
                        {
                            "period": normalized["period"],
                            "ward": normalized["ward"],
                            "category": normalized["category"],
                            "notes": normalized["notes"],
                        }
                    )

    except OSError as exc:
        raise RuntimeError(f"Failed to read dataset '{input_path}': {exc}") from exc

    return {
        "rows": rows,
        "distinct_wards": sorted(wards),
        "distinct_categories": sorted(categories),
        "null_rows": null_rows,
        "null_count": len(null_rows),
    }


def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for one ward and one category.
    """
    if not growth_type:
        raise ValueError("growth_type is required. Please specify --growth-type MoM or --growth-type YoY.")

    growth_type = growth_type.strip()
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Unsupported growth_type. Use MoM or YoY.")

    ward_text = (ward or "").strip()
    category_text = (category or "").strip()
    aggregate_tokens = {"all", "any", "*", "all wards", "all categories"}
    if not ward_text or ward_text.lower() in aggregate_tokens:
        raise ValueError("Refused: ward must be a single explicit ward; all-ward aggregation is not allowed.")
    if not category_text or category_text.lower() in aggregate_tokens:
        raise ValueError("Refused: category must be a single explicit category; mixed-category aggregation is not allowed.")

    filtered = [
        row
        for row in dataset["rows"]
        if row["ward"] == ward_text and row["category"] == category_text
    ]
    filtered.sort(key=lambda r: _parse_period(r["period"]))

    if not filtered:
        raise ValueError(f"No rows found for ward='{ward_text}' and category='{category_text}'.")

    by_period = {row["period"]: row for row in filtered}
    results = []

    for row in filtered:
        period = row["period"]
        current_actual = row["actual_spend"]
        comparison_period = _previous_period(period, growth_type)
        comparison_row = by_period.get(comparison_period)
        comparison_actual = comparison_row["actual_spend"] if comparison_row else None

        result = {
            "period": period,
            "ward": ward_text,
            "category": category_text,
            "actual_spend": "" if current_actual is None else f"{current_actual:.1f}",
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": "",
            "status": "",
            "reason": "",
            "comparison_period": comparison_period,
            "comparison_actual": "" if comparison_actual is None else f"{comparison_actual:.1f}",
            "null_note": row["notes"] if current_actual is None else "",
        }

        if current_actual is None:
            result["status"] = "FLAGGED_NULL"
            result["reason"] = "Current period actual_spend is null; growth not computed."
            if row["notes"]:
                result["reason"] += f" Note: {row['notes']}"
            results.append(result)
            continue

        if comparison_row is None:
            result["status"] = "NOT_COMPUTABLE"
            result["reason"] = f"Comparison period {comparison_period} not available in filtered data."
            results.append(result)
            continue

        if comparison_actual is None:
            result["status"] = "FLAGGED_NULL"
            result["reason"] = f"Comparison period {comparison_period} actual_spend is null; growth not computed."
            if comparison_row.get("notes"):
                result["reason"] += f" Note: {comparison_row['notes']}"
            results.append(result)
            continue

        if comparison_actual == 0:
            result["status"] = "NOT_COMPUTABLE"
            result["reason"] = "Comparison actual_spend is zero; division by zero avoided."
            results.append(result)
            continue

        growth_value = ((current_actual - comparison_actual) / comparison_actual) * 100.0
        result["status"] = "COMPUTED"
        result["formula"] = f"(({current_actual:.1f} - {comparison_actual:.1f}) / {comparison_actual:.1f}) * 100"
        result["growth_percent"] = f"{growth_value:.1f}"
        result["reason"] = "Computed using explicit growth formula."
        results.append(result)

    return results


def _write_output(output_path: str, rows: list):
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "reason",
        "comparison_period",
        "comparison_actual",
        "null_note",
    ]
    try:
        with open(output_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except OSError as exc:
        raise RuntimeError(f"Failed to write output '{output_path}': {exc}") from exc

def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward name")
    parser.add_argument("--category", required=True, help="Single category name")
    parser.add_argument("--growth-type", dest="growth_type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth output CSV")
    args = parser.parse_args()

    dataset = load_dataset(args.input)

    print(f"Detected {dataset['null_count']} rows with null actual_spend.")
    for null_row in dataset["null_rows"]:
        note = null_row["notes"] or "No note provided"
        print(
            f"NULL -> period={null_row['period']}, ward={null_row['ward']}, "
            f"category={null_row['category']}, note={note}"
        )

    growth_rows = compute_growth(
        dataset=dataset,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )
    _write_output(args.output, growth_rows)
    print(f"Done. Results written to {args.output}")

if __name__ == "__main__":
    main()
