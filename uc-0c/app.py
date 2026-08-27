"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
from datetime import datetime


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def _parse_period(value: str):
    return datetime.strptime(value, "%Y-%m")


def load_dataset(input_path: str) -> tuple[list[dict], list[dict]]:
    """Load and validate dataset; return rows and explicit null rows."""
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("Input CSV has no header.")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        rows = list(reader)

    null_rows = [
        row
        for row in rows
        if not (row.get("actual_spend") or "").strip()
    ]
    return rows, null_rows


def compute_growth(rows: list[dict], ward: str, category: str, growth_type: str) -> list[dict]:
    """Compute growth for one ward+category subset with explicit formula trace."""
    if growth_type not in {"MoM", "YoY"}:
        raise ValueError("growth_type must be either 'MoM' or 'YoY'.")

    scoped = [
        row for row in rows
        if row.get("ward") == ward and row.get("category") == category
    ]
    if not scoped:
        raise ValueError("No rows found for the given ward and category.")

    scoped.sort(key=lambda r: _parse_period(r["period"]))

    results = []
    for idx, row in enumerate(scoped):
        period = row["period"]
        actual_raw = (row.get("actual_spend") or "").strip()
        budget_raw = (row.get("budgeted_amount") or "").strip()

        record = {
            "period": period,
            "ward": ward,
            "category": category,
            "budgeted_amount": budget_raw,
            "actual_spend": actual_raw,
            "previous_actual": "",
            "growth_type": growth_type,
            "formula": "",
            "growth_percent": "",
            "status": "",
            "null_reason": (row.get("notes") or "").strip(),
        }

        prev_idx = idx - 1 if growth_type == "MoM" else idx - 12
        if prev_idx < 0:
            record["status"] = "NO_BASELINE"
            results.append(record)
            continue

        prev_row = scoped[prev_idx]
        prev_actual_raw = (prev_row.get("actual_spend") or "").strip()
        record["previous_actual"] = prev_actual_raw

        if not actual_raw:
            record["status"] = "NULL_ROW"
            record["formula"] = "NULL current actual_spend => growth not computed"
            results.append(record)
            continue

        if not prev_actual_raw:
            record["status"] = "PREVIOUS_NULL"
            record["formula"] = "NULL previous actual_spend => growth not computed"
            results.append(record)
            continue

        current = float(actual_raw)
        previous = float(prev_actual_raw)
        if previous == 0:
            record["status"] = "PREVIOUS_ZERO"
            record["formula"] = "(current - previous) / previous * 100; previous is 0"
            results.append(record)
            continue

        growth = ((current - previous) / previous) * 100
        record["formula"] = f"(({current:.2f} - {previous:.2f}) / {previous:.2f}) * 100"
        record["growth_percent"] = f"{growth:.2f}"
        record["status"] = "OK"
        results.append(record)

    return results


def write_output(output_path: str, rows: list[dict]):
    fields = [
        "period",
        "ward",
        "category",
        "budgeted_amount",
        "actual_spend",
        "previous_actual",
        "growth_type",
        "formula",
        "growth_percent",
        "status",
        "null_reason",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="UC-0C Growth Calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Exact ward name")
    parser.add_argument("--category", required=True, help="Exact category name")
    parser.add_argument("--growth-type", required=True, help="MoM or YoY")
    parser.add_argument("--output", required=True, help="Path to output CSV")
    args = parser.parse_args()

    rows, null_rows = load_dataset(args.input)
    print(f"Detected null actual_spend rows: {len(null_rows)}")
    for row in null_rows:
        print(
            "NULL_FLAG "
            f"period={row.get('period')} | ward={row.get('ward')} | "
            f"category={row.get('category')} | reason={row.get('notes', '').strip()}"
        )

    growth_rows = compute_growth(rows, args.ward, args.category, args.growth_type)
    write_output(args.output, growth_rows)
    print(f"Done. Growth table written to {args.output}")

if __name__ == "__main__":
    main()
