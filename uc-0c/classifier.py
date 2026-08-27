import csv
import os
import re


REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}


def load_dataset(filepath):
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append(row)
    except (IOError, csv.Error) as e:
        return {"error": f"Invalid file: {e}"}

    if not rows:
        return {"error": "Invalid file"}

    headers = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - headers
    if missing:
        return {"error": f"Invalid file: missing columns {sorted(missing)}"}

    null_details = []
    for row in rows:
        actual = row.get("actual_spend", "").strip()
        if actual == "":
            null_details.append({
                "period": row["period"],
                "ward": row["ward"],
                "category": row["category"],
                "reason": row.get("notes", "").strip() or "No reason provided",
            })

    return {
        "rows": rows,
        "null_count": len(null_details),
        "null_details": null_details,
    }


def _parse_period(period):
    parts = period.split("-")
    return int(parts[0]), int(parts[1])


def _period_label(period):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year, month = _parse_period(period)
    return f"{months[month - 1]} {year}"


def compute_growth(data_rows, growth_type):
    if not data_rows or isinstance(data_rows, dict):
        return {"error": "No data for the given ward and category."}

    if growth_type not in ("MoM", "YoY"):
        return {"error": "Invalid growth_type. Use MoM or YoY."}

    if growth_type == "MoM" and len(data_rows) < 2:
        return {"error": "Insufficient data for MoM calculation. Need at least 2 periods."}

    if growth_type == "YoY" and len(data_rows) < 13:
        return {"error": "Insufficient data for YoY calculation. Need at least 13 periods (12 months + 1)."}

    sorted_rows = sorted(data_rows, key=lambda r: r["period"])
    results = []

    for i, row in enumerate(sorted_rows):
        actual_str = row.get("actual_spend", "").strip()
        null_reason = None

        if actual_str == "":
            actual_val = None
            null_reason = row.get("notes", "").strip() or "No reason provided"
        else:
            actual_val = float(actual_str)

        budget_val = float(row["budgeted_amount"]) if row.get("budgeted_amount", "").strip() else None

        growth_rate = None
        formula = None

        if actual_val is None:
            growth_rate = "NULL"
            formula = "NULL (null actual_spend)"
        elif growth_type == "MoM":
            if i == 0:
                growth_rate = "N/A"
                formula = "Base period (no prior month)"
            else:
                prev_str = sorted_rows[i - 1].get("actual_spend", "").strip()
                if prev_str == "":
                    growth_rate = "NULL"
                    formula = "NULL (prior period has null actual_spend)"
                else:
                    prev_val = float(prev_str)
                    change = actual_val - prev_val
                    pct = (change / prev_val) * 100
                    growth_rate = f"{pct:+.1f}%"
                    formula = f"(({_period_label(row['period'])} - {_period_label(sorted_rows[i - 1]['period'])}) / {_period_label(sorted_rows[i - 1]['period'])}) * 100"
        elif growth_type == "YoY":
            if i < 12:
                growth_rate = "N/A"
                formula = "Base period (no prior year data)"
            else:
                prev_str = sorted_rows[i - 12].get("actual_spend", "").strip()
                if prev_str == "":
                    growth_rate = "NULL"
                    formula = "NULL (prior year period has null actual_spend)"
                else:
                    prev_val = float(prev_str)
                    change = actual_val - prev_val
                    pct = (change / prev_val) * 100
                    growth_rate = f"{pct:+.1f}%"
                    formula = f"(({_period_label(row['period'])} - {_period_label(sorted_rows[i - 12]['period'])}) / {_period_label(sorted_rows[i - 12]['period'])}) * 100"

        result_row = {
            "period": row["period"],
            "ward": row["ward"],
            "category": row["category"],
            "budgeted_amount": budget_val,
            "actual_spend": actual_val if actual_val is not None else "NULL",
            "growth_rate": growth_rate,
            "growth_type": growth_type,
            "formula": formula,
        }
        if null_reason:
            result_row["null_reason"] = null_reason

        results.append(result_row)

    return results


def validate_growth_request(data, ward, category, growth_type):
    if isinstance(data, dict) and "error" in data:
        return data

    if not growth_type:
        return {"error": "--growth-type is required. Specify MoM or YoY."}

    if not ward:
        return {"error": "--ward is required. Specify a ward name."}

    if not category:
        return {"error": "--category is required. Specify a category name."}

    wards = set(r["ward"] for r in data["rows"])
    if ward not in wards:
        return {"error": f"Ward '{ward}' not found. Available wards: {sorted(wards)}"}

    categories = set(r["category"] for r in data["rows"] if r["ward"] == ward)
    if category not in categories:
        return {"error": f"Category '{category}' not found for {ward}. Available categories: {sorted(categories)}"}

    return None


def run_growth_analysis(filepath, ward, category, growth_type):
    data = load_dataset(filepath)
    if isinstance(data, dict) and "error" in data:
        return data

    validation = validate_growth_request(data, ward, category, growth_type)
    if validation is not None:
        return validation

    filtered = [
        r for r in data["rows"]
        if r["ward"] == ward and r["category"] == category
    ]

    nulls = [d for d in data["null_details"] if d["ward"] == ward and d["category"] == category]

    growth_results = compute_growth(filtered, growth_type)
    if isinstance(growth_results, dict) and "error" in growth_results:
        return growth_results

    return {
        "ward": ward,
        "category": category,
        "growth_type": growth_type,
        "null_count_in_filter": len(nulls),
        "null_details": nulls,
        "results": growth_results,
    }
