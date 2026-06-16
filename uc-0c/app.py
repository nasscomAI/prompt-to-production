"""
UC-0C — Budget Growth Calculator
Computes month-over-month or year-over-year growth for a specific ward + category.
Enforcement rules in agents.md. Skills in skills.md.
"""
import argparse
import csv


def load_dataset(file_path: str) -> tuple[list[dict], str]:
    """
    Load budget CSV and report null rows.
    Returns (rows list, null_report str).
    """
    rows = []
    null_rows = []
    null_count = 0

    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row_num, row in enumerate(reader, start=2):  # start=2 because header is row 1
                rows.append(row)
                if not row.get("actual_spend", "").strip():
                    null_count += 1
                    null_rows.append({
                        "row_number": row_num,
                        "period": row.get("period", ""),
                        "ward": row.get("ward", ""),
                        "category": row.get("category", ""),
                        "reason": row.get("notes", "[No reason provided]"),
                    })
    except FileNotFoundError:
        raise FileNotFoundError(f"Budget file not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    null_report = f"Found {null_count} null actual_spend rows:\n"
    for nr in null_rows:
        null_report += f"  Row {nr['row_number']}: {nr['period']} | {nr['ward']} | {nr['category']} | Reason: {nr['reason']}\n"

    return rows, null_report


def compute_growth(
    rows: list[dict],
    ward: str,
    category: str,
    growth_type: str,
    null_periods: set[str],
) -> list[dict]:
    """
    Compute growth for a single ward-category pair.
    growth_type must be "MoM" or "YoY".
    Returns list of output rows with formula shown.
    """
    if growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Invalid growth_type '{growth_type}'. Must be 'MoM' or 'YoY'.")

    # Filter to the specified ward and category
    filtered = [
        r for r in rows
        if r.get("ward", "").strip() == ward and r.get("category", "").strip() == category
    ]

    if not filtered:
        raise KeyError(f"No data found for ward='{ward}', category='{category}'")

    # Sort by period
    filtered.sort(key=lambda r: r.get("period", ""))

    # Build output rows
    output = []
    prev_spend = None
    prev_period = None

    for row in filtered:
        period = row.get("period", "")
        period_key = f"{ward}|{category}|{period}"
        is_null = period_key in null_periods

        try:
            actual = float(row.get("actual_spend", "")) if row.get("actual_spend", "").strip() else None
        except ValueError:
            actual = None
            is_null = True

        if is_null or actual is None:
            output.append({
                "period": period,
                "actual_spend": "",
                "growth_value": "",
                "growth_percentage": "",
                "formula": "",
                "null_flag": f"NULL: {row.get('notes', '[No reason]')}",
            })
            prev_spend = None
            prev_period = period
            continue

        # Compute growth
        growth_val = None
        growth_pct = None
        formula_str = ""

        if growth_type == "MoM":
            if prev_spend is not None:
                growth_val = actual - prev_spend
                growth_pct = (growth_val / prev_spend * 100) if prev_spend != 0 else 0
                formula_str = f"MoM: ({actual:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
            else:
                formula_str = "MoM: [no previous month data]"

        elif growth_type == "YoY":
            # YoY: for simplicity, we compare consecutive non-null months
            # In a real scenario, you'd match same month across years
            if prev_spend is not None:
                growth_val = actual - prev_spend
                growth_pct = (growth_val / prev_spend * 100) if prev_spend != 0 else 0
                formula_str = f"YoY: ({actual:.1f} - {prev_spend:.1f}) / {prev_spend:.1f}"
            else:
                formula_str = "YoY: [no prior year same month data]"

        output.append({
            "period": period,
            "actual_spend": f"{actual:.1f}",
            "growth_value": f"{growth_val:.1f}" if growth_val is not None else "",
            "growth_percentage": f"{growth_pct:.1f}%" if growth_pct is not None else "",
            "formula": formula_str,
            "null_flag": "",
        })
        prev_spend = actual
        prev_period = period

    return output


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Calculator")
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",   required=True, help="Ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforce scope: ward and category are mandatory
    if not args.ward or not args.category:
        raise ValueError("--ward and --category are required.")

    if args.growth_type not in ["MoM", "YoY"]:
        raise ValueError(f"Invalid --growth-type '{args.growth_type}'. Must be 'MoM' or 'YoY'.")

    # Load and report nulls
    rows, null_report = load_dataset(args.input)
    print(null_report)

    # Identify null periods for the specified ward-category
    null_periods = set()
    for row in rows:
        if (
            not row.get("actual_spend", "").strip()
            and row.get("ward", "").strip() == args.ward
            and row.get("category", "").strip() == args.category
        ):
            period = row.get("period", "")
            null_periods.add(f"{args.ward}|{args.category}|{period}")

    # Compute growth
    try:
        output_rows = compute_growth(rows, args.ward, args.category, args.growth_type, null_periods)
    except KeyError as e:
        raise ValueError(str(e))
    except ValueError as e:
        raise e

    # Write output
    output_fields = ["period", "actual_spend", "growth_value", "growth_percentage", "formula", "null_flag"]
    with open(args.output, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Done. Growth output written to {args.output}")


if __name__ == "__main__":
    main()
