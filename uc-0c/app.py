"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse

import csv
from datetime import datetime
from typing import List, Dict, Any, Optional


REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def load_dataset(path: str) -> List[Dict[str, Any]]:
    """Read CSV, validate columns, and return list of rows as dicts. Also prints null info."""
    rows: List[Dict[str, Any]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in headers]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        null_rows = []
        for r in reader:
            # normalize
            row = {k: (r.get(k, "").strip() if r.get(k) is not None else "") for k in headers}
            # keep original strings; we parse numbers later
            if row.get("actual_spend", "") == "":
                null_rows.append(row)
            rows.append(row)

    if null_rows:
        print(f"Found {len(null_rows)} null actual_spend rows:")
        for nr in null_rows:
            print(f" - period={nr.get('period')} ward={nr.get('ward')} category={nr.get('category')} notes={nr.get('notes')}")
    else:
        print("No null actual_spend rows found.")

    return rows


def parse_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return None


def compute_growth(rows: List[Dict[str, Any]], ward: str, category: str, growth_type: str) -> List[Dict[str, Any]]:
    """Compute growth per period for given ward and category. Returns list of output rows.

    Enforcements:
    - refuses aggregation across wards/categories (ward and category must be specific)
    - flags null actual_spend rows and does not compute growth for them
    - shows formula used per output row
    """
    if not ward or not category:
        raise ValueError("Both ward and category must be specified.")
    if ward.lower() == "any" or category.lower() == "any":
        raise ValueError("Refusing to aggregate across wards or categories. Provide specific ward and category.")

    if growth_type not in ("MoM", "YoY"):
        raise ValueError("Unsupported growth_type. Supported: MoM, YoY")

    # filter rows
    filtered = [r for r in rows if r.get("ward") == ward and r.get("category") == category]
    if not filtered:
        raise ValueError("No rows found for given ward/category")

    # sort by period
    def period_key(r: Dict[str, Any]):
        try:
            return datetime.strptime(r.get("period", ""), "%Y-%m")
        except Exception:
            return datetime.min

    filtered.sort(key=period_key)

    outputs: List[Dict[str, Any]] = []
    prev_actual: Optional[float] = None
    prev_period: Optional[str] = None
    for r in filtered:
        period = r.get("period")
        budgeted = parse_float(r.get("budgeted_amount", ""))
        actual = parse_float(r.get("actual_spend", ""))
        notes = r.get("notes", "")

        out: Dict[str, Any] = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budgeted if budgeted is not None else "",
            "actual_spend": actual if actual is not None else "",
            "formula": "",
            "growth_percent": "",
            "flag": "",
            "notes": notes,
        }

        # If actual is null, flag and skip computation
        if actual is None:
            out["flag"] = "null_actual"
            out["formula"] = "(current - previous) / previous * 100"
            outputs.append(out)
            prev_actual = None
            prev_period = period
            continue

        # compute MoM: (current - previous)/previous*100
        if growth_type == "MoM":
            out["formula"] = "(current - previous) / previous * 100"
            if prev_actual is None:
                out["flag"] = "no_prev"
                out["growth_percent"] = ""
            else:
                if prev_actual == 0:
                    out["flag"] = "div_by_zero_prev"
                    out["growth_percent"] = ""
                else:
                    growth = (actual - prev_actual) / prev_actual * 100
                    out["growth_percent"] = round(growth, 1)
        else:
            # placeholder for YoY if needed
            out["formula"] = "(current - previous_year_same_month) / previous_year_same_month * 100"
            out["flag"] = "not_implemented"

        outputs.append(out)
        prev_actual = actual
        prev_period = period

    return outputs


def write_output(path: str, rows: List[Dict[str, Any]]):
    fieldnames = ["period", "ward", "category", "budgeted_amount", "actual_spend", "growth_percent", "formula", "flag", "notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="UC-0C — compute growth per ward/category from ward_budget.csv")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Ward name (exact match). Refuses 'Any'.")
    parser.add_argument("--category", required=True, help="Category name (exact match). Refuses 'Any'.")
    parser.add_argument("--growth-type", required=True, help="Growth type: MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforcement: refuse if growth-type not specified handled by argparse; additionally check values
    if args.ward.lower() == "any" or args.category.lower() == "any":
        print("Refusing to aggregate across wards or categories. Provide specific ward and category.")
        return

    # load
    rows = load_dataset(args.input)

    # compute
    out_rows = compute_growth(rows, args.ward, args.category, args.growth_type)

    # write
    write_output(args.output, out_rows)
    print(f"Done. Results written to {args.output}")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
