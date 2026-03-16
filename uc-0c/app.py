"""
UC-0C app.py — Starter file.
Build this using the RICE + agents.md + skills.md + CRAFT workflow.
See README.md for run command and expected behaviour.
"""
import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REQUIRED_COLUMNS: Tuple[str, ...] = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)


def _parse_period(period: str) -> Tuple[int, int]:
    s = (period or "").strip()
    parts = s.split("-")
    if len(parts) != 2:
        raise ValueError(f"Invalid period '{period}'. Expected YYYY-MM.")
    year_s, month_s = parts
    year = int(year_s)
    month = int(month_s)
    if month < 1 or month > 12:
        raise ValueError(f"Invalid period '{period}'. Month must be 01-12.")
    return year, month


def _format_period(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


def _previous_month(period: str) -> str:
    year, month = _parse_period(period)
    if month == 1:
        return _format_period(year - 1, 12)
    return _format_period(year, month - 1)


def _previous_year(period: str) -> str:
    year, month = _parse_period(period)
    return _format_period(year - 1, month)


def _to_float_or_none(value: str) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s == "":
        return None
    return float(s)


@dataclass(frozen=True)
class Row:
    period: str
    ward: str
    category: str
    budgeted_amount: float
    actual_spend: Optional[float]
    notes: str


def load_dataset(path: str) -> Tuple[List[Row], List[Row]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with p.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV appears to be empty or missing a header row.")

        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"CSV missing required columns: {missing}. Expected at least: {list(REQUIRED_COLUMNS)}"
            )

        rows: List[Row] = []
        null_rows: List[Row] = []
        for i, r in enumerate(reader, start=2):
            period = (r.get("period") or "").strip()
            ward = (r.get("ward") or "").strip()
            category = (r.get("category") or "").strip()
            notes = (r.get("notes") or "").strip()

            if not period or not ward or not category:
                raise ValueError(f"Row {i}: period/ward/category must be non-empty.")
            _parse_period(period)

            budgeted_amount = _to_float_or_none(r.get("budgeted_amount"))
            if budgeted_amount is None:
                raise ValueError(f"Row {i}: budgeted_amount must be present.")

            actual_spend = _to_float_or_none(r.get("actual_spend"))

            row = Row(
                period=period,
                ward=ward,
                category=category,
                budgeted_amount=float(budgeted_amount),
                actual_spend=actual_spend,
                notes=notes,
            )
            rows.append(row)
            if actual_spend is None:
                null_rows.append(row)

    return rows, null_rows


def _refuse_aggregation(ward: Optional[str], category: Optional[str]) -> None:
    ward_given = ward is not None and ward.strip() != ""
    category_given = category is not None and category.strip() != ""

    if ward_given != category_given:
        raise ValueError(
            "Refusing: must specify both --ward and --category for a single series, "
            "or specify neither to compute all ward+category series (no aggregation)."
        )

    for label, v in (("ward", ward), ("category", category)):
        if v is None:
            continue
        s = v.strip()
        if s.lower() in {"any", "all", "*"}:
            raise ValueError(
                f"Refusing: '--{label} {v}' implies aggregation. Provide an explicit {label} value."
            )


def _group_rows(rows: Sequence[Row]) -> Dict[Tuple[str, str], List[Row]]:
    grouped: Dict[Tuple[str, str], List[Row]] = {}
    for r in rows:
        grouped.setdefault((r.ward, r.category), []).append(r)
    for k in list(grouped.keys()):
        grouped[k].sort(key=lambda rr: _parse_period(rr.period))
    return grouped


def compute_growth(
    rows: Sequence[Row],
    ward: Optional[str],
    category: Optional[str],
    growth_type: str,
) -> List[Dict[str, str]]:
    gt = (growth_type or "").strip()
    if gt == "":
        raise ValueError("Refusing: --growth-type is required (e.g., MoM or YoY).")
    if gt not in {"MoM", "YoY"}:
        raise ValueError("Invalid --growth-type. Expected one of: MoM, YoY.")

    _refuse_aggregation(ward, category)

    grouped = _group_rows(rows)

    if ward and category:
        key = (ward.strip(), category.strip())
        if key not in grouped:
            raise ValueError(
                f"Unknown ward+category pair: ward='{ward}' category='{category}'."
            )
        keys = [key]
    else:
        keys = sorted(grouped.keys())

    out: List[Dict[str, str]] = []
    for (w, c) in keys:
        series = grouped[(w, c)]
        by_period: Dict[str, Row] = {r.period: r for r in series}

        for r in series:
            null_reason = r.notes if r.actual_spend is None else ""
            flags: List[str] = []

            if gt == "MoM":
                prior_period = _previous_month(r.period)
                formula = "MoM: (curr_actual - prev_actual) / prev_actual"
            else:
                prior_period = _previous_year(r.period)
                formula = "YoY: (curr_actual - prior_year_actual) / prior_year_actual"

            curr = r.actual_spend
            prev_row = by_period.get(prior_period)
            prev = prev_row.actual_spend if prev_row is not None else None

            growth_value: Optional[float] = None
            if curr is None:
                flags.append("NULL_actual_spend")
            if prev_row is None:
                flags.append(f"missing_prior_period:{prior_period}")
            elif prev is None:
                flags.append(f"NULL_prior_actual_spend:{prior_period}")
            elif prev == 0:
                flags.append(f"prior_actual_spend_zero:{prior_period}")

            if not flags:
                growth_value = (curr - prev) / prev  # type: ignore[operator]

            out.append(
                {
                    "period": r.period,
                    "ward": w,
                    "category": c,
                    "actual_spend": "" if curr is None else f"{curr:.6g}",
                    "growth_type": gt,
                    "growth_value": ""
                    if growth_value is None
                    else f"{growth_value * 100:.6g}",  # percent
                    "formula": formula,
                    "flags": "|".join(flags),
                    "null_reason": null_reason,
                }
            )

    return out


def _write_output_csv(path: str, rows: Iterable[Dict[str, str]]) -> None:
    p = Path(path)
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth_value",
        "formula",
        "flags",
        "null_reason",
    ]
    with p.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main() -> None:
    parser = argparse.ArgumentParser(description="UC-0C growth calculator")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--ward", required=False, help="Ward name (must pair with --category)")
    parser.add_argument(
        "--category", required=False, help="Category name (must pair with --ward)"
    )
    parser.add_argument(
        "--growth-type",
        dest="growth_type",
        required=False,
        help="Growth type: MoM or YoY (required; refusal if missing)",
    )
    parser.add_argument("--output", required=True, help="Output CSV path")

    args = parser.parse_args()

    try:
        data, null_rows = load_dataset(args.input)

        if null_rows:
            print(
                f"Found {len(null_rows)} NULL actual_spend rows (will be flagged; growth not computed for these periods):",
                file=sys.stderr,
            )
            for r in null_rows:
                print(
                    f"- {r.period} · {r.ward} · {r.category} · {r.notes}",
                    file=sys.stderr,
                )

        output_rows = compute_growth(
            data,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
        )
        _write_output_csv(args.output, output_rows)
    except Exception as e:
        print(str(e), file=sys.stderr)
        raise SystemExit(2)

if __name__ == "__main__":
    main()
