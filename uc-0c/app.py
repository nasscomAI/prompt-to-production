"""
UC-0C app.py — Budget growth-computation agent.

Implements the skills in skills.md (load_dataset -> compute_growth) and enforces
the contract in agents.md: produce a per-ward per-category per-period growth
table (never a single aggregated number), flag every null actual_spend row with
its notes reason, show the formula on every row, and refuse rather than guess.

Usage:
  python3 app.py \
    --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" \
    --category "Roads & Pothole Repair" \
    --growth-type MoM \
    --output growth_output.csv
"""
import argparse
import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
SUPPORTED_GROWTH = {"MoM"}


class DatasetError(Exception):
    pass


def load_dataset(path):
    """Skill: load_dataset. Read CSV, validate columns, report null rows."""
    rows = []
    null_rows = []
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not all(
            c in reader.fieldnames for c in REQUIRED_COLUMNS
        ):
            missing = [
                c for c in REQUIRED_COLUMNS
                if c not in (reader.fieldnames or [])
            ]
            raise DatasetError(
                "missing required columns: " + ", ".join(missing or reader.fieldnames or ["none"])
            )
        for line_no, row in enumerate(reader, start=2):
            actual = row["actual_spend"].strip()
            if actual == "":
                null_rows.append(
                    {
                        "period": row["period"].strip(),
                        "ward": row["ward"].strip(),
                        "category": row["category"].strip(),
                        "notes": row["notes"].strip(),
                        "line": line_no,
                    }
                )
                row["actual_spend"] = None
            else:
                row["actual_spend"] = float(actual)
            row["period"] = row["period"].strip()
            row["ward"] = row["ward"].strip()
            row["category"] = row["category"].strip()
            row["notes"] = row["notes"].strip()
            rows.append(row)
    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """Skill: compute_growth. Per-period growth table for one ward+category."""
    filtered = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not filtered:
        raise DatasetError(f"no data for ward '{ward}' and category '{category}'")

    ordered = sorted(filtered, key=lambda r: r["period"])
    out = []
    if growth_type == "MoM":
        formula = "growth = (actual_spend[t] - actual_spend[t-1]) / actual_spend[t-1] * 100"
    else:
        raise DatasetError(f"unsupported growth type: {growth_type}")

    prev_spend = None
    for r in ordered:
        cur_spend = r["actual_spend"]
        if cur_spend is None:
            out.append(
                {
                    "period": r["period"],
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_percent": "",
                    "formula": formula,
                    "notes": f"NULL - not computed. Reason: {r['notes']}",
                }
            )
            continue
        if prev_spend is not None and prev_spend != 0:
            growth = (cur_spend - prev_spend) / prev_spend * 100
        else:
            growth = None
        out.append(
            {
                "period": r["period"],
                "ward": ward,
                "category": category,
                "actual_spend": f"{cur_spend:.1f}",
                "growth_percent": (
                    f"{growth:+.1f}" if growth is not None else "n/a"
                ),
                "formula": formula,
                "notes": r["notes"],
            }
        )
        prev_spend = cur_spend
    return out


def main():
    parser = argparse.ArgumentParser(description="UC-0C budget growth agent")
    parser.add_argument("--input", required=True)
    parser.add_argument("--ward", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--growth-type", required=True, help="MoM (YoY unsupported: no prior-year data)")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if not Path(args.input).exists():
        sys.stderr.write(f"Refusal: input file not found: {args.input}\n")
        sys.exit(1)

    growth_type = args.growth_type
    if not growth_type:
        sys.stderr.write("Refusal: --growth-type not specified; please provide MoM.\n")
        sys.exit(1)
    if growth_type not in SUPPORTED_GROWTH:
        sys.stderr.write(
            f"Refusal: growth type '{growth_type}' unsupported — only MoM is "
            f"computable from a single calendar year of data.\n"
        )
        sys.exit(1)

    try:
        rows, null_rows = load_dataset(args.input)
    except DatasetError as e:
        sys.stderr.write(f"Refusal: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Refusal: could not read dataset: {e}\n")
        sys.exit(1)

    if null_rows:
        print(f"Flagging {len(null_rows)} null actual_spend row(s):")
        for n in null_rows:
            print(
                f"  - {n['period']} | {n['ward']} | {n['category']}"
                f" | reason: {n['notes']}"
            )

    try:
        table = compute_growth(rows, args.ward, args.category, growth_type)
    except DatasetError as e:
        sys.stderr.write(f"Refusal: {e}\n")
        sys.exit(1)

    fieldnames = ["period", "ward", "category", "actual_spend", "growth_percent", "formula", "notes"]
    with Path(args.output).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(table)

    print(f"Wrote {len(table)} rows to {args.output} (formula: MoM)")


if __name__ == "__main__":
    main()
