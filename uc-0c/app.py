"""
UC-0C — Per-ward per-category growth with explicit formulas and null handling.
See README.md for run command.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = ("period", "ward", "category", "budgeted_amount", "actual_spend", "notes")


def load_dataset(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read CSV, validate columns, return (all rows, null rows with blank actual_spend)."""
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row")
        for col in REQUIRED_COLUMNS:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column {col!r}; found {reader.fieldnames}")

        rows: list[dict[str, Any]] = []
        null_rows: list[dict[str, Any]] = []
        for row in reader:
            rows.append(row)
            raw = (row.get("actual_spend") or "").strip()
            if raw == "":
                null_rows.append(row)
    return rows, null_rows


def parse_float(s: str) -> float | None:
    t = (s or "").strip()
    if t == "":
        return None
    return float(t)


def period_key(p: str) -> tuple[int, int]:
    y, m = p.split("-")
    return int(y), int(m)


def prev_month(period: str) -> str | None:
    y, m = period_key(period)
    if m == 1:
        return f"{y - 1}-12"
    return f"{y}-{m - 1:02d}"


def prev_year_month(period: str) -> str | None:
    y, m = period_key(period)
    return f"{y - 1}-{m:02d}"


def compute_growth(
    rows: list[dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> list[dict[str, str]]:
    """Build growth rows for one ward/category series."""
    series = [r for r in rows if r["ward"] == ward and r["category"] == category]
    by_period = {r["period"]: r for r in series}
    periods_sorted = sorted(by_period.keys())

    out: list[dict[str, str]] = []
    for period in periods_sorted:
        row = by_period[period]
        cur = parse_float(row["actual_spend"])
        formula = ""
        growth_pct = ""
        prior_p = ""
        prior_val_s = ""
        note = ""

        if growth_type == "MoM":
            pp = prev_month(period)
            if pp is None or pp not in by_period:
                formula = "MoM = ((current - previous_month) / previous_month) * 100"
                note = "No prior month in series"
            else:
                prev_raw = by_period[pp]["actual_spend"]
                prev = parse_float(prev_raw)
                prior_p = pp
                prior_val_s = prev_raw.strip() if prev_raw else ""
                formula = "MoM = ((current - previous_month) / previous_month) * 100"
                if cur is None or prev is None:
                    note = "Cannot compute: current or prior actual_spend is null"
                elif prev == 0:
                    note = "Cannot compute: prior month actual_spend is zero"
                else:
                    growth_pct = f"{((cur - prev) / prev) * 100:+.1f}%"

        elif growth_type == "YoY":
            py = prev_year_month(period)
            formula = "YoY = ((current - same_month_prior_year) / same_month_prior_year) * 100"
            if py is None or py not in by_period:
                note = "Same month in prior year not present in dataset"
            else:
                prev_raw = by_period[py]["actual_spend"]
                prev = parse_float(prev_raw)
                prior_p = py
                prior_val_s = prev_raw.strip() if prev_raw else ""
                if cur is None or prev is None:
                    note = "Cannot compute: current or prior-year actual_spend is null"
                elif prev == 0:
                    note = "Cannot compute: prior-year actual_spend is zero"
                else:
                    growth_pct = f"{((cur - prev) / prev) * 100:+.1f}%"
        else:
            raise ValueError(f"Unknown growth type: {growth_type!r}")

        out.append(
            {
                "row_type": "growth",
                "period": period,
                "ward": ward,
                "category": category,
                "growth_type": growth_type,
                "actual_spend": row["actual_spend"].strip() if row["actual_spend"] else "",
                "prior_period": prior_p,
                "prior_actual_spend": prior_val_s,
                "growth_pct": growth_pct,
                "formula": formula,
                "notes": note,
            }
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Ward budget growth (MoM / YoY) with null audit.")
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--ward", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--growth-type", required=True, choices=("MoM", "YoY"))
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    rows, null_rows = load_dataset(args.input)

    out_rows: list[dict[str, str]] = []
    fields = [
        "row_type",
        "period",
        "ward",
        "category",
        "growth_type",
        "actual_spend",
        "prior_period",
        "prior_actual_spend",
        "growth_pct",
        "formula",
        "notes",
    ]

    for nr in null_rows:
        out_rows.append(
            {
                "row_type": "null_flag",
                "period": nr["period"],
                "ward": nr["ward"],
                "category": nr["category"],
                "growth_type": "",
                "actual_spend": "",
                "prior_period": "",
                "prior_actual_spend": "",
                "growth_pct": "NULL",
                "formula": "n/a — actual_spend missing",
                "notes": (nr.get("notes") or "").strip(),
            }
        )

    out_rows.extend(compute_growth(rows, args.ward, args.category, args.growth_type))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)


if __name__ == "__main__":
    main()
