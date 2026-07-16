"""
UC-0C app.py — Budget Growth Calculator
"""
import argparse
import csv
import os
import re


def normalize_string(val: str) -> str:
    """
    Normalizes string by converting to lowercase, replacing en-dash/em-dash with standard hyphens,
    and compressing whitespace.
    """
    if not val:
        return ""
    # Replace en-dash (\u2013) and em-dash (\u2014) with standard hyphen
    normalized = val.replace("\u2013", "-").replace("\u2014", "-")
    # Compress multiple spaces and strip
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized.lower()


def load_dataset(input_path: str) -> list:
    """
    Reads the CSV file, validates columns, counts and reports all null actual_spend rows.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    dataset = []
    required_cols = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

    with open(input_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = set(reader.fieldnames or [])

        # Validate columns
        missing = required_cols - headers
        if missing:
            raise ValueError(f"Missing required columns in CSV: {missing}")

        null_rows = []
        for i, row in enumerate(reader, start=2):  # line numbers start at 2 (1 is header)
            actual_spend_raw = row["actual_spend"].strip()
            # If empty, it's a null row
            if not actual_spend_raw:
                null_rows.append((i, row))
            dataset.append(row)

    print(f"Total rows loaded: {len(dataset)}")
    print(f"Deliberate null actual_spend rows found: {len(null_rows)}")
    for line_num, r in null_rows:
        print(f"  Line {line_num} | Period: {r['period']} | Ward: {r['ward']} | Category: {r['category']} | Reason: {r['notes']}")

    return dataset


def compute_growth(dataset: list, ward: str, category: str, growth_type: str) -> list:
    """
    Computes period-over-period growth for a specific ward and category, flagging nulls.
    """
    if not growth_type:
        raise ValueError("Error: --growth-type must be specified. Please choose MoM or YoY.")
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Error: Invalid --growth-type '{growth_type}'. Must be MoM or YoY.")

    if not ward or normalize_string(ward) in ["any", "all", "none"]:
        raise ValueError("Error: Aggregation across all/any wards is not permitted. Please specify a single valid ward.")

    if not category or normalize_string(category) in ["any", "all", "none"]:
        raise ValueError("Error: Aggregation across all/any categories is not permitted. Please specify a single valid category.")

    # Find the exact ward and category names in dataset
    norm_target_ward = normalize_string(ward)
    norm_target_category = normalize_string(category)

    actual_ward = None
    actual_category = None

    for row in dataset:
        if normalize_string(row["ward"]) == norm_target_ward:
            actual_ward = row["ward"]
        if normalize_string(row["category"]) == norm_target_category:
            actual_category = row["category"]

    if not actual_ward:
        valid_wards = sorted(list(set(row["ward"] for row in dataset)))
        raise ValueError(f"Error: Ward '{ward}' not found in dataset. Valid wards are: {valid_wards}")
    if not actual_category:
        valid_categories = sorted(list(set(row["category"] for row in dataset)))
        raise ValueError(f"Error: Category '{category}' not found in dataset. Valid categories are: {valid_categories}")

    # Filter rows matching the target ward and category
    filtered_rows = []
    for row in dataset:
        if row["ward"] == actual_ward and row["category"] == actual_category:
            filtered_rows.append(row)

    # Sort rows by period (chronological order)
    filtered_rows.sort(key=lambda x: x["period"])

    results = []
    period_to_row = {row["period"]: row for row in filtered_rows}

    for index, row in enumerate(filtered_rows):
        period = row["period"]
        actual_spend_str = row["actual_spend"].strip()
        notes = row["notes"].strip()

        # Flag current null row
        if not actual_spend_str:
            results.append({
                "period": period,
                "ward": actual_ward,
                "category": actual_category,
                "actual_spend": "NULL",
                "growth": f"NULL - {notes}",
                "formula": "N/A (actual spend is null)"
            })
            continue

        current_spend = float(actual_spend_str)

        # Parse previous period key based on growth type
        if growth_type == "MoM":
            # Extract year and month from YYYY-MM
            match = re.match(r"^(\d{4})-(\d{2})$", period)
            if not match:
                results.append({
                    "period": period,
                    "ward": actual_ward,
                    "category": actual_category,
                    "actual_spend": str(current_spend),
                    "growth": "N/A",
                    "formula": f"N/A (invalid period format '{period}')"
                })
                continue
            year, month = int(match.group(1)), int(match.group(2))
            # Subtract 1 month
            prev_month = month - 1
            prev_year = year
            if prev_month == 0:
                prev_month = 12
                prev_year = year - 1
            prev_period = f"{prev_year:04d}-{prev_month:02d}"
        else:  # YoY
            match = re.match(r"^(\d{4})-(\d{2})$", period)
            if not match:
                results.append({
                    "period": period,
                    "ward": actual_ward,
                    "category": actual_category,
                    "actual_spend": str(current_spend),
                    "growth": "N/A",
                    "formula": f"N/A (invalid period format '{period}')"
                })
                continue
            year, month = int(match.group(1)), int(match.group(2))
            prev_period = f"{(year - 1):04d}-{month:02d}"

        # Get previous row
        prev_row = period_to_row.get(prev_period)

        if not prev_row:
            # First period in dataset or no historical data
            results.append({
                "period": period,
                "ward": actual_ward,
                "category": actual_category,
                "actual_spend": str(current_spend),
                "growth": "N/A",
                "formula": f"N/A (no data for previous period {prev_period})"
            })
            continue

        prev_spend_str = prev_row["actual_spend"].strip()
        if not prev_spend_str:
            # Previous month is null
            prev_notes = prev_row["notes"].strip()
            results.append({
                "period": period,
                "ward": actual_ward,
                "category": actual_category,
                "actual_spend": str(current_spend),
                "growth": f"NULL - Previous period ({prev_period}) is null: {prev_notes}",
                "formula": "N/A (previous spend is null)"
            })
            continue

        prev_spend = float(prev_spend_str)

        # Compute growth percentage
        if prev_spend == 0:
            if current_spend == 0:
                growth_val = 0.0
                growth_str = "0.0%"
                formula_str = "((0.0 - 0.0) / 0.0) * 100"
            else:
                growth_str = "N/A (previous spend is zero)"
                formula_str = f"(({current_spend} - 0.0) / 0.0) * 100"
        else:
            growth_val = ((current_spend - prev_spend) / prev_spend) * 100
            formula_str = f"(({current_spend} - {prev_spend}) / {prev_spend}) * 100"
            if growth_val > 0:
                growth_str = f"+{growth_val:.1f}%"
            elif growth_val < 0:
                # Format with standard negative sign
                growth_str = f"-{abs(growth_val):.1f}%"
            else:
                growth_str = "0.0%"

        results.append({
            "period": period,
            "ward": actual_ward,
            "category": actual_category,
            "actual_spend": str(current_spend),
            "growth": growth_str,
            "formula": formula_str
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to input ward budget CSV file")
    parser.add_argument("--ward", required=True, help="Specific ward to analyze")
    parser.add_argument("--category", required=True, help="Specific category to analyze")
    parser.add_argument("--growth-type", help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write output CSV file")
    args = parser.parse_args()

    # Load dataset
    dataset = load_dataset(args.input)

    # Compute growth
    results = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output to CSV
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["period", "ward", "category", "actual_spend", "growth", "formula"])
        writer.writeheader()
        writer.writerows(results)

    print(f"Growth calculation written to {args.output}")


if __name__ == "__main__":
    main()
