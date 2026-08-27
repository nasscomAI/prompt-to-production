"""
UC-0C app.py — Budget growth calculator.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
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

VALID_GROWTH_TYPES = {"MoM"}


def normalize_text(value: str) -> str:
    """Normalize text, fix mojibake, and remove extra whitespace/newlines."""
    if value is None:
        return ""

    text = str(value).replace("\ufeff", "")

    # Try to repair common mojibake safely
    try:
        repaired = text.encode("latin1").decode("utf-8")
        text = repaired
    except Exception:
        pass

    replacements = {
        "â€“": "-",
        "a€“": "-",
        "å€“": "-",
        "€“": "-",
        "a€\"": "-",
        "â€”": "-",
        "a€”": "-",
        "–": "-",
        "—": "-",
        "\r": " ",
        "\n": " ",
        "\t": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = " ".join(text.split())
    return text.strip()


def load_dataset(input_path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Load the CSV, validate required columns, and return:
    1) all rows
    2) rows with null actual_spend
    """
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")

        normalized_fieldnames = [normalize_text(col) for col in reader.fieldnames]
        fieldnames_set = set(normalized_fieldnames)

        missing = REQUIRED_COLUMNS - fieldnames_set
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        rows: List[Dict[str, str]] = []
        null_rows: List[Dict[str, str]] = []

        for raw_row in reader:
            clean_row = {}
            for original_key, value in raw_row.items():
                clean_key = normalize_text(original_key)
                clean_row[clean_key] = normalize_text(value)

            rows.append(clean_row)

            if clean_row.get("actual_spend", "") == "":
                null_rows.append(clean_row)

    return rows, null_rows


def parse_float(value: str) -> float:
    return float(normalize_text(value))


def compute_mom_growth(previous_value: float, current_value: float) -> float:
    return ((current_value - previous_value) / previous_value) * 100.0


def filter_rows(rows: List[Dict[str, str]], ward: str, category: str) -> List[Dict[str, str]]:
    ward_clean = normalize_text(ward)
    category_clean = normalize_text(category)

    filtered = [
        row for row in rows
        if normalize_text(row["ward"]) == ward_clean and normalize_text(row["category"]) == category_clean
    ]
    return sorted(filtered, key=lambda r: normalize_text(r["period"]))


def compute_growth(
    rows: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Return a per-period table for the specified ward and category.
    Null rows are flagged and not computed.
    """
    ward = normalize_text(ward)
    category = normalize_text(category)
    growth_type = normalize_text(growth_type)

    if not growth_type:
        raise ValueError("growth_type is required. Refusing to guess.")

    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"Unsupported growth_type: {growth_type}. Supported: MoM")

    if ward.lower() in {"all", "all wards", "any"}:
        raise ValueError("Refusing all-ward aggregation. Specify a single ward.")

    if category.lower() in {"all", "all categories", "any"}:
        raise ValueError("Refusing all-category aggregation. Specify a single category.")

    filtered_rows = filter_rows(rows, ward, category)
    if not filtered_rows:
        raise ValueError("No rows found for the specified ward and category.")

    output_rows: List[Dict[str, str]] = []
    previous_valid_spend = None
    previous_valid_period = None

    for row in filtered_rows:
        period = normalize_text(row["period"])
        actual_spend_raw = normalize_text(row["actual_spend"])
        notes = normalize_text(row["notes"])

        out_row = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend_lakh": actual_spend_raw if actual_spend_raw else "NULL",
            "growth_type": growth_type,
            "formula_used": "",
            "growth_result_percent": "",
            "status": "",
            "null_reason": "",
        }

        if actual_spend_raw == "":
            out_row["status"] = "NULL_FLAGGED"
            out_row["null_reason"] = notes
            out_row["formula_used"] = "Not computed due to null actual_spend"
            out_row["growth_result_percent"] = "NA"
            output_rows.append(out_row)
            continue

        current_spend = parse_float(actual_spend_raw)

        if previous_valid_spend is None:
            out_row["status"] = "BASE_PERIOD"
            out_row["formula_used"] = "No previous valid month available"
            out_row["growth_result_percent"] = "NA"
        else:
            if previous_valid_spend == 0:
                out_row["status"] = "NOT_COMPUTED"
                out_row["formula_used"] = (
                    f"MoM = ((current - previous) / previous) * 100; previous period {previous_valid_period} = 0"
                )
                out_row["growth_result_percent"] = "NA"
            else:
                growth = compute_mom_growth(previous_valid_spend, current_spend)
                out_row["status"] = "COMPUTED"
                out_row["formula_used"] = (
                    f"MoM = (({current_spend:.1f} - {previous_valid_spend:.1f}) / {previous_valid_spend:.1f}) * 100"
                )
                out_row["growth_result_percent"] = f"{growth:+.1f}"

        output_rows.append(out_row)
        previous_valid_spend = current_spend
        previous_valid_period = period

    return output_rows


def write_output(output_path: str, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend_lakh",
        "growth_type",
        "formula_used",
        "growth_result_percent",
        "status",
        "null_reason",
    ]

    cleaned_rows = []
    for row in rows:
        cleaned_rows.append({
            "period": normalize_text(row.get("period", "")),
            "ward": normalize_text(row.get("ward", "")),
            "category": normalize_text(row.get("category", "")),
            "actual_spend_lakh": normalize_text(row.get("actual_spend_lakh", "")),
            "growth_type": normalize_text(row.get("growth_type", "")),
            "formula_used": normalize_text(row.get("formula_used", "")),
            "growth_result_percent": normalize_text(row.get("growth_result_percent", "")),
            "status": normalize_text(row.get("status", "")),
            "null_reason": normalize_text(row.get("null_reason", "")),
        })

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
        )
        writer.writeheader()
        writer.writerows(cleaned_rows)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="Growth type, e.g. MoM")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)

    result_rows = compute_growth(
        rows=rows,
        ward=args.ward,
        category=args.category,
        growth_type=args.growth_type,
    )

    write_output(args.output, result_rows)

    print(f"Done. Output written to {args.output}")
    print(f"Dataset null actual_spend rows detected: {len(null_rows)}")


if __name__ == "__main__":
    main()