"""
UC-0C app.py — Per-ward per-category growth analyst with null flagging
and refusal of all-ward aggregation.

Usage:
    python app.py \
        --input ../data/budget/ward_budget.csv \
        --ward "Ward 1 – Kasba" \
        --category "Roads & Pothole Repair" \
        --growth-type MoM \
        --output growth_output.csv
"""
import argparse
import csv
import sys
from typing import Dict, List, Tuple

VALID_GROWTH_TYPES = {"MoM", "QoQ", "YoY"}

REQUIRED_COLS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]


def fail(msg: str) -> "None":
    sys.stderr.write(f"UC-0C: {msg}\n")
    sys.exit(1)


# --- skill: load_dataset ----------------------------------------------------

def load_dataset(path: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                fail(f"input CSV has no header: {path}")
            missing = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
            if missing:
                fail(f"input CSV missing required columns: {missing}")
            rows = list(reader)
    except FileNotFoundError:
        fail(f"input file not found: {path}")
    except OSError as e:
        fail(f"cannot read input file {path}: {e}")

    if not rows:
        fail(f"input CSV has no data rows: {path}")

    null_report: List[Dict[str, str]] = []
    for r in rows:
        if (r.get("actual_spend") or "").strip() == "":
            null_report.append({
                "period": r.get("period", ""),
                "ward": r.get("ward", ""),
                "category": r.get("category", ""),
                "notes": r.get("notes", ""),
            })

    return rows, null_report


# --- skill: compute_growth --------------------------------------------------

def _formula(growth_type: str) -> str:
    return "(current - previous) / previous * 100"


def _prior_period(period: str, growth_type: str) -> str:
    y, m = period.split("-")
    y, m = int(y), int(m)
    if growth_type == "MoM":
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    elif growth_type == "QoQ":
        m -= 3
        while m <= 0:
            m += 12
            y -= 1
    elif growth_type == "YoY":
        y -= 1
    return f"{y:04d}-{m:02d}"


def compute_growth(
    rows: List[Dict[str, str]],
    null_report: List[Dict[str, str]],
    ward: str,
    category: str,
    growth_type: str,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    if growth_type not in VALID_GROWTH_TYPES:
        fail(f"invalid --growth-type {growth_type!r}; must be one of {sorted(VALID_GROWTH_TYPES)}")

    series = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not series:
        fail(f"no rows found for ward={ward!r} category={category!r}")
    extra_wards = {r["ward"] for r in rows}
    extra_cats = {r["category"] for r in rows}
    if len(extra_wards) > 1 or len(extra_cats) > 1:
        if (ward not in extra_wards) or (category not in extra_cats):
            fail("refusing to aggregate: (ward, category) not found uniquely in dataset")

    series_nulls = [n for n in null_report if n["ward"] == ward and n["category"] == category]
    series.sort(key=lambda r: r["period"])
    by_period = {r["period"]: r for r in series}

    out: List[Dict[str, str]] = []
    for r in series:
        period = r["period"]
        actual = (r.get("actual_spend") or "").strip()
        prior_period = _prior_period(period, growth_type)
        prior_row = by_period.get(prior_period)
        prior_spend = (prior_row.get("actual_spend") or "").strip() if prior_row else ""

        growth_value = ""
        note = ""
        if actual == "":
            note = "null flagged; growth not computed"
        elif prior_spend == "" or prior_row is None:
            note = f"no prior period ({prior_period}) actual_spend; growth not computed"
        else:
            try:
                cur = float(actual)
                prv = float(prior_spend)
            except ValueError:
                note = "non-numeric spend value; growth not computed"
            else:
                if prv == 0:
                    note = "prior period actual_spend is zero; growth not computed (division by zero)"
                else:
                    growth_value = f"{(cur - prv) / prv * 100:+.1f}%"

        out.append({
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": actual if actual else "NULL",
            "prior_period": prior_period,
            "prior_spend": prior_spend if prior_spend else "NULL",
            "growth_value": growth_value,
            "growth_type": growth_type,
            "formula": _formula(growth_type),
            "note": note,
        })

    return out, series_nulls


# --- entrypoint -------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C per-ward per-category growth")
    parser.add_argument("--input", required=True, help="path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="exact ward name, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="exact category name")
    parser.add_argument("--growth-type", required=True, choices=sorted(VALID_GROWTH_TYPES),
                        help="one of MoM, QoQ, YoY")
    parser.add_argument("--output", required=True, help="path to write growth_output.csv")
    args = parser.parse_args()

    rows, null_report = load_dataset(args.input)
    out_rows, series_nulls = compute_growth(
        rows, null_report, args.ward, args.category, args.growth_type
    )

    try:
        with open(args.output, "w", encoding="utf-8", newline="") as f:
            f.write(f"# null_flag_report: {len(series_nulls)} null row(s) in series "
                    f"ward={args.ward!r} category={args.category!r}\n")
            for n in series_nulls:
                f.write(f"# NULL {n['period']} {n['ward']} {n['category']} :: {n['notes']}\n")
            fieldnames = ["period", "ward", "category", "actual_spend", "prior_period",
                          "prior_spend", "growth_value", "growth_type", "formula", "note"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in out_rows:
                writer.writerow(r)
    except OSError as e:
        fail(f"cannot write output file {args.output}: {e}")


if __name__ == "__main__":
    main()
