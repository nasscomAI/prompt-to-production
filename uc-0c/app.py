"""
UC-0C — Budget growth computation.
Implements load_dataset and compute_growth as defined in agents.md and skills.md.
"""
import argparse
import csv
from typing import Dict, List, Tuple


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def _parse_float(value: str):
    value = (value or "").strip()
    if value == "":
        return None
    return float(value)


def _should_refuse_aggregation(value: str) -> bool:
    token = (value or "").strip().lower()
    return token in {"all", "*", "any", "all wards", "all categories", "aggregate", "overall"}


def load_dataset(input_path: str) -> Tuple[List[Dict[str, object]], List[Dict[str, str]]]:
    """
    skill: load_dataset
    Reads CSV, validates columns, and reports all rows where actual_spend is null.
    """
    with open(input_path, "r", newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        columns = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        rows: List[Dict[str, object]] = []
        null_rows: List[Dict[str, str]] = []

        for row in reader:
            normalized = {
                "period": (row.get("period") or "").strip(),
                "ward": (row.get("ward") or "").strip(),
                "category": (row.get("category") or "").strip(),
                "budgeted_amount": _parse_float(row.get("budgeted_amount", "")),
                "actual_spend": _parse_float(row.get("actual_spend", "")),
                "notes": (row.get("notes") or "").strip(),
            }

            if normalized["actual_spend"] is None:
                null_rows.append(
                    {
                        "period": normalized["period"],
                        "ward": normalized["ward"],
                        "category": normalized["category"],
                        "notes": normalized["notes"],
                    }
                )

            rows.append(normalized)

    return rows, null_rows


def compute_growth(
    rows: List[Dict[str, object]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, object]]:
    """
    skill: compute_growth
    Computes per-period growth for one ward + one category with formula in every row.
    """
    if not growth_type:
        raise ValueError("Missing required argument: --growth-type. Specify MoM or YoY.")

    if _should_refuse_aggregation(ward) or _should_refuse_aggregation(category):
        raise ValueError("Refused: aggregation across wards or categories is not allowed unless explicitly instructed.")

    normalized_growth = growth_type.strip().upper()
    if normalized_growth not in {"MOM", "YOY"}:
        raise ValueError("Invalid --growth-type. Allowed values: MoM, YoY.")

    filtered = [
        r for r in rows if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise ValueError("No rows found for the provided ward and category.")

    filtered.sort(key=lambda x: x["period"])
    by_period = {r["period"]: r for r in filtered}

    output_rows: List[Dict[str, object]] = []
    for idx, row in enumerate(filtered):
        period = row["period"]
        current = row["actual_spend"]
        formula = ""
        growth_value = ""
        status = "OK"
        flag_reason = ""

        if current is None:
            status = "FLAGGED_NULL"
            flag_reason = f"actual_spend is null. notes: {row['notes'] or 'No reason provided'}"
            formula = "Not computed due to null actual_spend"
        else:
            if normalized_growth == "MOM":
                if idx == 0:
                    status = "NO_BASELINE"
                    flag_reason = "No previous month available for MoM."
                    formula = "MoM growth % = (current - previous_month) / previous_month * 100"
                else:
                    prev_row = filtered[idx - 1]
                    prev_value = prev_row["actual_spend"]
                    formula = "MoM growth % = (current - previous_month) / previous_month * 100"

                    if prev_value is None:
                        status = "FLAGGED_PREV_NULL"
                        flag_reason = (
                            "Previous month actual_spend is null. "
                            f"previous notes: {prev_row['notes'] or 'No reason provided'}"
                        )
                    elif prev_value == 0:
                        status = "FLAGGED_PREV_ZERO"
                        flag_reason = "Previous month actual_spend is zero; division undefined."
                    else:
                        growth_num = ((current - prev_value) / prev_value) * 100
                        growth_value = f"{growth_num:.1f}%"

            if normalized_growth == "YOY":
                previous_year_period = f"{int(period[:4]) - 1}-{period[5:7]}"
                formula = "YoY growth % = (current - same_month_last_year) / same_month_last_year * 100"
                reference = by_period.get(previous_year_period)

                if reference is None:
                    status = "NO_BASELINE"
                    flag_reason = f"No reference period found for {previous_year_period}."
                else:
                    reference_value = reference["actual_spend"]
                    if reference_value is None:
                        status = "FLAGGED_PREV_NULL"
                        flag_reason = (
                            "Reference period actual_spend is null. "
                            f"reference notes: {reference['notes'] or 'No reason provided'}"
                        )
                    elif reference_value == 0:
                        status = "FLAGGED_PREV_ZERO"
                        flag_reason = "Reference period actual_spend is zero; division undefined."
                    else:
                        growth_num = ((current - reference_value) / reference_value) * 100
                        growth_value = f"{growth_num:.1f}%"

        output_rows.append(
            {
                "period": period,
                "ward": ward,
                "category": category,
                "budgeted_amount": row["budgeted_amount"],
                "actual_spend": current,
                "growth_type": "MoM" if normalized_growth == "MOM" else "YoY",
                "formula": formula,
                "growth_result": growth_value,
                "status": status,
                "flag_reason": flag_reason,
                "notes": row["notes"],
            }
        )

    return output_rows


def _write_output(output_path: str, output_rows: List[Dict[str, object]]):
    fieldnames = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "growth_type",
        "formula",
        "growth_result",
        "status",
        "flag_reason",
        "notes",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (single ward only)")
    parser.add_argument("--category", required=True, help="Category name (single category only)")
    parser.add_argument("--growth-type", required=False, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows from {args.input}")
    print(f"Detected {len(null_rows)} row(s) with null actual_spend before computation")
    for null_row in null_rows:
        print(
            "NULL_ROW "
            f"period={null_row['period']} "
            f"ward={null_row['ward']} "
            f"category={null_row['category']} "
            f"notes={null_row['notes'] or 'No reason provided'}"
        )

    output_rows = compute_growth(rows, args.ward, args.category, args.growth_type or "")
    _write_output(args.output, output_rows)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
