"""
UC-0C — Growth computation CLI

Implements `load_dataset` and `compute_growth` per `skills.md` and
enforcement rules in `agents.md`.

Run (example):
python classifier.py \
  --input ../data/budget/ward_budget.csv \
  --ward "Ward 1 – Kasba" \
  --category "Roads & Pothole Repair" \
  --growth-type MoM \
  --output growth_output.csv
"""
from __future__ import annotations
import argparse
import csv
import os
import sys
from typing import List, Dict, Tuple, Optional
from datetime import datetime

REQUIRED_COLUMNS = [
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
]


def parse_period(period: str) -> datetime:
    return datetime.strptime(period, "%Y-%m")


def load_dataset(input_path: str) -> Tuple[Optional[List[Dict]], List[Dict], List[str]]:
    """
    Reads CSV at `input_path` and validates required columns.

    Returns: (dataset, null_report, validation_errors)
    - dataset: list of rows (dict) with `actual_spend` normalized to float or None
    - null_report: list of rows where `actual_spend` is None
    - validation_errors: list of error messages (empty on success)
    """
    if not os.path.exists(input_path):
        return None, [], [f"Input file not found: {input_path}"]

    dataset: List[Dict] = []
    null_report: List[Dict] = []
    validation_errors: List[str] = []

    try:
        with open(input_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            headers = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in headers]
            if missing:
                validation_errors.append(f"Missing required columns: {', '.join(missing)}")
                return None, [], validation_errors

            for row in reader:
                r = dict(row)
                raw = r.get("actual_spend", "")
                if raw is None or raw.strip() == "":
                    r["actual_spend"] = None
                    null_report.append({
                        "period": r.get("period"),
                        "ward": r.get("ward"),
                        "category": r.get("category"),
                        "notes": r.get("notes", ""),
                    })
                else:
                    try:
                        # allow numeric strings with commas
                        value = float(raw.replace(",", ""))
                        r["actual_spend"] = value
                    except Exception:
                        # treat unparsable as null but report
                        r["actual_spend"] = None
                        null_report.append({
                            "period": r.get("period"),
                            "ward": r.get("ward"),
                            "category": r.get("category"),
                            "notes": f"unparsable actual_spend: {raw}",
                        })

                dataset.append(r)

    except Exception as e:
        validation_errors.append(f"Failed reading CSV: {e}")
        return None, [], validation_errors

    return dataset, null_report, validation_errors


def compute_growth(dataset: List[Dict], ward: str, category: str, growth_type: str) -> Tuple[List[Dict], Dict]:
    """
    Compute growth for rows matching `ward` and `category`.

    growth_type: 'MoM' or 'YoY'

    Returns: (results, meta)
    """
    if not growth_type:
        raise ValueError("Refusal: --growth-type is required (MoM or YoY).")

    growth_type = growth_type.upper()
    if growth_type not in ("MOM", "YOY"):
        raise ValueError("Refusal: unsupported growth-type. Use MoM or YoY.")

    # refusal on aggregation: ward and category must be specific
    if not ward or not category:
        raise ValueError("Refusal: both --ward and --category must be specified; aggregation is not allowed.")

    # filter dataset
    rows = [r for r in dataset if r.get("ward") == ward and r.get("category") == category]
    if not rows:
        return [], {"ward": ward, "category": category, "growth_type": growth_type, "note": "No matching rows"}

    # sort by period
    try:
        rows.sort(key=lambda r: parse_period(r.get("period")))
    except Exception:
        # fallback to lexical sort
        rows.sort(key=lambda r: r.get("period"))

    results: List[Dict] = []

    formula_text = ""
    if growth_type == "MOM":
        formula_text = "(this_period - prev_period) / prev_period * 100"
    else:
        formula_text = "(this_period - same_period_prev_year) / same_period_prev_year * 100"

    # create a map from period to actual for quick lookup (for YoY)
    period_to_actual = {r["period"]: r["actual_spend"] for r in rows}

    for idx, r in enumerate(rows):
        period = r.get("period")
        actual = r.get("actual_spend")
        null_flag = actual is None
        growth_value: Optional[float] = None

        if null_flag:
            # do not compute
            results.append({
                "period": period,
                "ward": ward,
                "category": category,
                "actual_spend": None,
                "growth": None,
                "formula": formula_text,
                "null_flag": True,
                "notes": r.get("notes", ""),
            })
            continue

        if growth_type == "MOM":
            # previous chronological row (index-1) if exists
            if idx == 0:
                growth_value = None
            else:
                prev_actual = rows[idx - 1].get("actual_spend")
                if prev_actual is None or prev_actual == 0:
                    growth_value = None
                else:
                    growth_value = (actual - prev_actual) / prev_actual * 100

        else:  # YOY
            # compute same month previous year by shifting YYYY-MM
            try:
                dt = parse_period(period)
                prev_year = dt.replace(year=dt.year - 1)
                key = prev_year.strftime("%Y-%m")
                prev_actual = period_to_actual.get(key)
                if prev_actual is None or prev_actual == 0:
                    growth_value = None
                else:
                    growth_value = (actual - prev_actual) / prev_actual * 100
            except Exception:
                growth_value = None

        results.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual,
            "growth": None if growth_value is None else round(growth_value, 4),
            "formula": formula_text,
            "null_flag": False,
            "notes": r.get("notes", ""),
        })

    meta = {"ward": ward, "category": category, "growth_type": growth_type, "formula": formula_text}
    return results, meta


def write_output(output_path: str, results: List[Dict]):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth", "formula", "null_flag", "notes"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow({k: r.get(k) for k in fieldnames})
    except Exception as e:
        print(f"Failed to write output: {e}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth computation")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (no aggregation)")
    parser.add_argument("--category", required=True, help="Category name (no aggregation)")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    dataset, null_report, errors = load_dataset(args.input)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)

    # report null rows before computing
    if null_report:
        print(f"Found {len(null_report)} null actual_spend rows:")
        for nr in null_report:
            print(f" - {nr['period']} · {nr['ward']} · {nr['category']} · notes: {nr.get('notes','')}")

    try:
        results, meta = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except ValueError as ve:
        print(str(ve), file=sys.stderr)
        sys.exit(3)

    if not results:
        print("No results produced (no matching rows).", file=sys.stderr)
        sys.exit(4)

    write_output(args.output, results)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()
