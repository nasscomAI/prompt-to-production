"""
UC-0C app.py — Per-ward per-category growth calculator.

Behaviour:
- Loads `ward_budget.csv`, validates required columns, reports null rows.
- Refuses when `--growth-type` is not provided.
- Computes month-on-month (MoM) growth for the specified ward and category,
  shows the formula used for each computed row, and writes a CSV with flags
  for null rows (no growth computed for nulls).
"""
import argparse
import csv
from typing import List, Dict, Tuple, Optional
from datetime import datetime


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """Read CSV and validate columns. Return rows and list of missing columns (if any)."""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in cols]
        rows = list(reader)
    return rows, missing


def _parse_period(p: str) -> datetime:
    return datetime.strptime(p, "%Y-%m")


def compute_growth(rows: List[Dict[str, str]], ward: str, category: str, growth_type: str) -> List[Dict[str, str]]:
    """Filter rows for ward+category and compute MoM growth.

    Returns list of dicts with keys: period, ward, category, actual_spend, growth_pct, formula, null_flag, null_reason
    """
    if growth_type is None:
        raise ValueError("--growth-type is required; refuse to guess")
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("Unsupported growth-type. Supported: MoM, YoY")

    filtered = [r for r in rows if r.get("ward", "").strip() == ward and r.get("category", "").strip() == category]
    # Sort by period
    filtered.sort(key=lambda r: _parse_period(r["period"]))

    output = []
    prev_value: Optional[float] = None
    prev_period: Optional[str] = None

    for r in filtered:
        period = r.get("period", "")
        actual_raw = r.get("actual_spend", "").strip()
        notes = r.get("notes", "").strip()
        row_out = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual_raw,
            "growth_pct": "",
            "formula": "",
            "null_flag": "",
            "null_reason": "",
        }

        if actual_raw == "" or actual_raw.upper() == "NULL":
            row_out["null_flag"] = "TRUE"
            row_out["null_reason"] = notes or ""
            prev_value = None
            prev_period = None
            output.append(row_out)
            continue

        try:
            actual = float(actual_raw)
        except Exception:
            row_out["null_flag"] = "TRUE"
            row_out["null_reason"] = f"Invalid actual_spend value: {actual_raw}"
            prev_value = None
            prev_period = None
            output.append(row_out)
            continue

        if growth_type == "MoM":
            if prev_value is None:
                # cannot compute growth for first period
                row_out["growth_pct"] = ""
                row_out["formula"] = "(no previous month)"
            else:
                if prev_value == 0:
                    row_out["growth_pct"] = "undefined"
                    row_out["formula"] = f"(curr - prev) / prev where prev=0 -> undefined (prev from {prev_period})"
                else:
                    growth = (actual - prev_value) / prev_value * 100.0
                    row_out["growth_pct"] = f"{growth:.1f}%"
                    row_out["formula"] = f"({actual} - {prev_value}) / {prev_value}"
        else:
            # YoY not implemented for small dataset; keep placeholder
            row_out["growth_pct"] = "" 
            row_out["formula"] = "(YoY not implemented)"

        prev_value = actual
        prev_period = period
        output.append(row_out)

    return output


def write_output(path: str, rows: List[Dict[str, str]]):
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula", "null_flag", "null_reason"]
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth calculator per ward/category")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact)")
    parser.add_argument("--category", required=True, help="Category name (exact)")
    parser.add_argument("--growth-type", required=False, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, missing = load_dataset(args.input)
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")

    if not args.growth_type:
        raise SystemExit("Error: --growth-type is required; refuse to guess")

    if args.ward.strip().lower() == "any" or args.category.strip().lower() == "any":
        raise SystemExit("Refuse to aggregate across wards or categories. Provide specific ward and category.")

    out_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, out_rows)


if __name__ == "__main__":
    main()
