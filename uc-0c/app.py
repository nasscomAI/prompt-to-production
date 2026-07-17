"""
UC-0C — Ward-budget growth calculator
Implements load_dataset and compute_growth per agents.md / skills.md.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = (
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
)

SUPPORTED_GROWTH_TYPES = ("MoM", "YoY")

# Phrases that imply cross-ward / cross-category aggregation — refuse these.
AGGREGATION_PATTERNS = (
    re.compile(r"^all$", re.I),
    re.compile(r"^all[\s_-]?wards?$", re.I),
    re.compile(r"^all[\s_-]?categor(?:y|ies)$", re.I),
    re.compile(r"^city[\s_-]?wide$", re.I),
    re.compile(r"^across[\s_-]?wards?$", re.I),
    re.compile(r"^total$", re.I),
    re.compile(r"^aggregate$", re.I),
    re.compile(r"^\*$"),
)

GROWTH_LABELS = {
    "MoM": "MoM",
    "YoY": "YoY",
}


class GrowthError(ValueError):
    """Raised when input is invalid, ambiguous, or violates enforcement rules."""


def _parse_spend(raw: str | None) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise GrowthError(f"Invalid actual_spend value: {raw!r}") from exc


def _looks_like_aggregation(value: str) -> bool:
    text = value.strip()
    return any(p.match(text) for p in AGGREGATION_PATTERNS)


def _shift_period(period: str, months: int) -> str | None:
    """Shift YYYY-MM by months; return None if malformed."""
    match = re.fullmatch(r"(\d{4})-(\d{2})", period.strip())
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2))
    if not 1 <= month <= 12:
        return None
    idx = year * 12 + (month - 1) + months
    new_year, new_month0 = divmod(idx, 12)
    return f"{new_year:04d}-{new_month0 + 1:02d}"


def _format_growth(pct: float) -> str:
    """Format signed percentage to one decimal, matching README references."""
    rounded = round(pct, 1)
    if rounded > 0:
        return f"+{rounded:.1f}%"
    return f"{rounded:.1f}%"


def _fmt_val(value: float | None, *, missing: str = "null") -> str:
    """Render a spend value for the formula; use a placeholder when absent."""
    if value is None:
        return missing
    return f"{value:g}"


def _build_formula(
    growth_type: str,
    current: float | None,
    previous: float | None,
    *,
    prev_missing: str,
    result: str | None = None,
) -> str:
    """
    Build the formula string with the actual processed values substituted in,
    e.g. "MoM: (19.7 − 14.8) / 14.8 × 100 = +33.1%".
    """
    label = GROWTH_LABELS[growth_type]
    cur = _fmt_val(current)
    prev = _fmt_val(previous, missing=prev_missing)
    expr = f"{label}: ({cur} − {prev}) / {prev} × 100"
    if result is not None:
        expr = f"{expr} = {result}"
    return expr


def load_dataset(input_path: str | Path) -> dict[str, Any]:
    """
    Read the ward-budget CSV, validate columns, and report null actual_spend.

    Returns:
        {
          "rows": [dict, ...],  # actual_spend as float | None
          "null_report": {
            "null_count": int,
            "null_rows": [
              {"period", "ward", "category", "notes"},
              ...
            ],
          },
        }
    """
    path = Path(input_path)
    if not path.exists():
        raise GrowthError(f"Input file not found: {path}")
    if not path.is_file():
        raise GrowthError(f"Input path is not a file: {path}")

    try:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise GrowthError(f"Input file is empty or has no header: {path}")
            fields = [f.strip() for f in reader.fieldnames]
            missing = [c for c in REQUIRED_COLUMNS if c not in fields]
            if missing:
                raise GrowthError(
                    "Missing required columns: "
                    f"{missing}. Expected schema: {list(REQUIRED_COLUMNS)}"
                )
            raw_rows = list(reader)
    except OSError as exc:
        raise GrowthError(f"Input file unreadable: {path}") from exc

    if not raw_rows:
        raise GrowthError(f"Input file has no data rows: {path}")

    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, str]] = []
    for raw in raw_rows:
        spend = _parse_spend(raw.get("actual_spend"))
        notes = (raw.get("notes") or "").strip()
        row = {
            "period": (raw.get("period") or "").strip(),
            "ward": (raw.get("ward") or "").strip(),
            "category": (raw.get("category") or "").strip(),
            "budgeted_amount": (raw.get("budgeted_amount") or "").strip(),
            "actual_spend": spend,
            "notes": notes,
        }
        rows.append(row)
        if spend is None:
            null_rows.append(
                {
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": notes or "(no reason given in notes)",
                }
            )

    return {
        "rows": rows,
        "null_report": {
            "null_count": len(null_rows),
            "null_rows": null_rows,
        },
    }


def _print_null_report(null_report: dict[str, Any]) -> None:
    count = null_report["null_count"]
    print(f"Null actual_spend rows: {count}", file=sys.stderr)
    for item in null_report["null_rows"]:
        print(
            f"  FLAGGED NULL · {item['period']} · {item['ward']} · "
            f"{item['category']} · reason: {item['notes']}",
            file=sys.stderr,
        )


def compute_growth(
    dataset: dict[str, Any],
    ward: str,
    category: str,
    growth_type: str,
    output_path: str | Path,
) -> list[dict[str, Any]]:
    """
    Compute per-period growth for one ward × one category; write output CSV.

    Returns the list of output row dicts.
    """
    if not growth_type or not str(growth_type).strip():
        raise GrowthError(
            "--growth-type is required. Specify MoM or YoY — refusing to guess."
        )

    growth_type_norm = str(growth_type).strip()
    # Accept common case variants but keep canonical labels.
    growth_lookup = {g.lower(): g for g in SUPPORTED_GROWTH_TYPES}
    if growth_type_norm.lower() not in growth_lookup:
        raise GrowthError(
            f"Unsupported growth_type {growth_type_norm!r}. "
            f"Supported: {', '.join(SUPPORTED_GROWTH_TYPES)} — refusing to guess."
        )
    growth_type_canon = growth_lookup[growth_type_norm.lower()]

    ward = ward.strip()
    category = category.strip()
    if not ward or not category:
        raise GrowthError(
            "Both --ward and --category are required. "
            "Refusing all-ward or cross-category aggregation."
        )
    if _looks_like_aggregation(ward) or _looks_like_aggregation(category):
        raise GrowthError(
            "All-ward / cross-category aggregation is not allowed. "
            "Provide one specific ward and one specific category."
        )

    if not dataset or "rows" not in dataset:
        raise GrowthError("Dataset is missing or malformed — refusing to compute.")

    filtered = [
        r
        for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]
    if not filtered:
        raise GrowthError(
            f"No rows for ward={ward!r} category={category!r}. "
            "Refusing to broaden the filter."
        )

    filtered = sorted(filtered, key=lambda r: r["period"])
    by_period = {r["period"]: r for r in filtered}

    lag_months = 1 if growth_type_canon == "MoM" else 12
    output_rows: list[dict[str, Any]] = []

    for row in filtered:
        period = row["period"]
        current = row["actual_spend"]
        notes = row["notes"]
        prev_period = _shift_period(period, -lag_months)
        prev_row = by_period.get(prev_period) if prev_period else None
        previous = prev_row["actual_spend"] if prev_row is not None else None

        # Placeholder used for the previous value when no prior row exists at
        # all (distinct from a prior row whose actual_spend is null).
        prev_missing = "null" if prev_row is not None else "n/a"

        out: dict[str, Any] = {
            "period": period,
            "ward": ward,
            "category": category,
            "actual_spend": "" if current is None else current,
            "growth_pct": "",
            "status": "",
            "formula": _build_formula(
                growth_type_canon, current, previous, prev_missing=prev_missing
            ),
            "notes": "",
        }

        if current is None:
            out["status"] = "FLAGGED_NULL"
            out["notes"] = notes or "(no reason given in notes)"
            out["growth_pct"] = ""
            output_rows.append(out)
            continue

        if prev_row is None:
            out["status"] = "NO_BASELINE"
            out["notes"] = (
                f"No prior period ({prev_period or 'n/a'}) for {growth_type_canon}; "
                "growth not computed"
            )
            output_rows.append(out)
            continue

        if previous is None:
            out["status"] = "FLAGGED_PREV_NULL"
            prev_notes = prev_row.get("notes") or "(no reason given in notes)"
            out["notes"] = (
                f"Prior period {prev_period} has null actual_spend "
                f"(reason: {prev_notes}); growth not computed"
            )
            output_rows.append(out)
            continue

        if previous == 0:
            out["status"] = "FLAGGED_DIV_ZERO"
            out["notes"] = (
                f"Prior period {prev_period} actual_spend is 0; growth not computed"
            )
            output_rows.append(out)
            continue

        pct = (current - previous) / previous * 100.0
        result = _format_growth(pct)
        out["growth_pct"] = result
        out["formula"] = _build_formula(
            growth_type_canon, current, previous, prev_missing=prev_missing, result=result
        )
        out["status"] = "OK"
        output_rows.append(out)

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_pct",
        "status",
        "formula",
        "notes",
    ]
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    return output_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "UC-0C: Per-ward per-category budget growth calculator "
            "(no cross-ward aggregation; nulls flagged; formula shown)."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv (e.g. ../data/budget/ward_budget.csv)",
    )
    parser.add_argument(
        "--ward",
        required=True,
        help='Exact ward name (e.g. "Ward 1 – Kasba")',
    )
    parser.add_argument(
        "--category",
        required=True,
        help='Exact category name (e.g. "Roads & Pothole Repair")',
    )
    parser.add_argument(
        "--growth-type",
        required=True,
        dest="growth_type",
        help="Growth formula to use: MoM or YoY (required — never guessed)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path (e.g. growth_output.csv)",
    )
    args = parser.parse_args()

    try:
        dataset = load_dataset(args.input)
        _print_null_report(dataset["null_report"])
        rows = compute_growth(
            dataset,
            ward=args.ward,
            category=args.category,
            growth_type=args.growth_type,
            output_path=args.output,
        )
    except GrowthError as exc:
        raise SystemExit(f"error: {exc}") from exc

    print(f"Wrote {len(rows)} period rows to {args.output}")
    flagged = sum(1 for r in rows if r["status"].startswith("FLAGGED"))
    print(f"Flagged (not computed): {flagged}")


if __name__ == "__main__":
    main()
