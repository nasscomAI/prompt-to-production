"""
UC-0C app.py — Per-ward per-category budget growth calculator.
Built from agents.md (RICE) + skills.md: load_dataset, compute_growth.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REQUIRED_COLUMNS = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)

SUPPORTED_GROWTH_TYPES = {"MoM"}


class GrowthError(Exception):
    """Refusal — wrong aggregation, missing growth type, or bad input."""


def load_dataset(input_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Skill: load_dataset
    Read CSV, validate columns, report null actual_spend rows before return.
    """
    path = Path(input_path)
    if not path.exists() or not path.is_file():
        raise GrowthError(f"Input file not found: {input_path}")

    try:
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise GrowthError("CSV has no header row.")
            missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
            if missing:
                raise GrowthError(f"Missing required columns: {', '.join(missing)}")
            rows = list(reader)
    except OSError as exc:
        raise GrowthError(f"Unable to read CSV: {exc}") from exc

    if not rows:
        raise GrowthError("CSV is empty — refuse to compute.")

    null_report: List[Dict[str, str]] = []
    for row in rows:
        spend_raw = (row.get("actual_spend") or "").strip()
        if spend_raw == "":
            null_report.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "notes": (row.get("notes") or "").strip() or "(no notes)",
                }
            )

    print(f"Null report: {len(null_report)} null actual_spend row(s)")
    for item in null_report:
        print(
            f"  - {item['period']} | {item['ward']} | {item['category']} "
            f"| reason: {item['notes']}"
        )

    return rows, null_report


def _parse_spend(value: str) -> Optional[float]:
    text = (value or "").strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def compute_growth(
    rows: List[Dict[str, Any]],
    ward: str,
    category: str,
    growth_type: str,
) -> List[Dict[str, str]]:
    """
    Skill: compute_growth
    Per-period table for one ward + one category; formula on every row.
    """
    if not growth_type or not str(growth_type).strip():
        raise GrowthError(
            "REFUSE: --growth-type not specified. "
            "Ask for an explicit type (supported: MoM). Never guess."
        )

    gt = growth_type.strip()
    if gt not in SUPPORTED_GROWTH_TYPES:
        raise GrowthError(
            f"REFUSE: unsupported growth-type '{gt}'. Supported: MoM."
        )

    if not ward or not str(ward).strip():
        raise GrowthError("REFUSE: --ward is required. Never aggregate all wards.")
    if not category or not str(category).strip():
        raise GrowthError(
            "REFUSE: --category is required. Never aggregate all categories."
        )

    # Guard against all-ward / cross-category requests phrased in the arg.
    ward_l = ward.strip().lower()
    cat_l = category.strip().lower()
    if ward_l in {"all", "all wards", "*"} or "all ward" in ward_l:
        raise GrowthError(
            "REFUSE: all-ward aggregation is not allowed. "
            "Provide a single ward name."
        )
    if cat_l in {"all", "all categories", "*"} or "all categor" in cat_l:
        raise GrowthError(
            "REFUSE: cross-category aggregation is not allowed. "
            "Provide a single category."
        )

    scoped = [
        r
        for r in rows
        if (r.get("ward") or "").strip() == ward.strip()
        and (r.get("category") or "").strip() == category.strip()
    ]
    if not scoped:
        raise GrowthError(
            f"REFUSE: no rows for ward='{ward}' category='{category}'. "
            "Do not broaden scope."
        )

    scoped.sort(key=lambda r: r.get("period") or "")

    formula_mom = "((current_actual - previous_actual) / previous_actual) * 100"
    output: List[Dict[str, str]] = []
    previous_spend: Optional[float] = None
    previous_period: Optional[str] = None

    for row in scoped:
        period = (row.get("period") or "").strip()
        spend = _parse_spend(row.get("actual_spend") or "")
        notes = (row.get("notes") or "").strip()

        if spend is None:
            output.append(
                {
                    "period": period,
                    "ward": ward.strip(),
                    "category": category.strip(),
                    "actual_spend": "NULL",
                    "growth_pct": "FLAGGED",
                    "formula": formula_mom if gt == "MoM" else gt,
                    "flag": "NULL_ACTUAL_SPEND",
                    "notes": notes or "(no notes)",
                }
            )
            # Null current — do not use as previous for next period.
            previous_spend = None
            previous_period = period
            continue

        if previous_spend is None:
            growth_pct = "N/A"
            flag = "NO_PREVIOUS" if previous_period is None else "PREVIOUS_NULL"
            note = (
                "First period in series — MoM not computed"
                if previous_period is None
                else f"Previous period {previous_period} had null actual_spend"
            )
        elif previous_spend == 0:
            growth_pct = "FLAGGED"
            flag = "DIVIDE_BY_ZERO"
            note = f"Previous actual_spend was 0 ({previous_period})"
        else:
            pct = ((spend - previous_spend) / previous_spend) * 100
            growth_pct = f"{pct:+.1f}%"
            flag = ""
            note = notes

        output.append(
            {
                "period": period,
                "ward": ward.strip(),
                "category": category.strip(),
                "actual_spend": f"{spend}",
                "growth_pct": growth_pct,
                "formula": formula_mom,
                "flag": flag,
                "notes": note,
            }
        )
        previous_spend = spend
        previous_period = period

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UC-0C: Per-ward per-category growth (refuse all-ward aggregation)."
    )
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument(
        "--ward",
        required=False,
        default=None,
        help="Exact ward name (required — no all-ward aggregation)",
    )
    parser.add_argument(
        "--category",
        required=False,
        default=None,
        help="Exact category name (required)",
    )
    parser.add_argument(
        "--growth-type",
        required=False,
        default=None,
        help="Growth type (required — e.g. MoM). Never guessed.",
    )
    parser.add_argument("--output", required=True, help="Path to growth_output.csv")
    args = parser.parse_args()

    try:
        if not args.growth_type:
            raise GrowthError(
                "REFUSE: --growth-type not specified. "
                "Provide MoM explicitly; never guess the formula."
            )
        if not args.ward:
            raise GrowthError(
                "REFUSE: --ward not specified. Never aggregate across all wards."
            )
        if not args.category:
            raise GrowthError(
                "REFUSE: --category not specified. Never aggregate across categories."
            )

        rows, _null_report = load_dataset(args.input)
        result = compute_growth(rows, args.ward, args.category, args.growth_type)
    except GrowthError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output)
    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_pct",
        "formula",
        "flag",
        "notes",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    print(f"Done. Wrote {len(result)} rows to {out_path}")


if __name__ == "__main__":
    main()
