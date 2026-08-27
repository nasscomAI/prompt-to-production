"""
UC-0C — Ward Budget Growth Calculator

Deterministic growth-computation tool that enforces the contracts in agents.md:
  - Refuses cross-ward or cross-category aggregation
  - Refuses to guess a growth formula (MoM/YoY must be named)
  - Flags every null actual_spend row instead of imputing or skipping
  - Shows arithmetic in the formula column on every computed row
"""
import argparse
import csv
import sys
from typing import Dict, List, Optional, Tuple

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount",
                    "actual_spend", "notes"]

AGGREGATION_TOKENS = {"all", "*", "aggregate", "any", "total", "sum"}

VALID_GROWTH_TYPES = {"MoM", "YoY"}


def load_dataset(path: str) -> Tuple[List[dict], List[dict]]:
    """Load and validate the ward-budget CSV."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required column(s): {', '.join(missing)}")

        rows: List[dict] = []
        nulls: List[dict] = []
        for i, raw in enumerate(reader, start=2):
            try:
                budgeted = float(raw["budgeted_amount"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Non-numeric budgeted_amount at row {i}: "
                    f"{raw.get('period')}/{raw.get('ward')}/{raw.get('category')}"
                )

            actual_raw = (raw.get("actual_spend") or "").strip()
            if actual_raw == "":
                actual: Optional[float] = None
            else:
                try:
                    actual = float(actual_raw)
                except ValueError:
                    raise ValueError(
                        f"Non-numeric actual_spend at row {i}: "
                        f"{raw.get('period')}/{raw.get('ward')}/{raw.get('category')} "
                        f"= {actual_raw!r}"
                    )

            row = {
                "period": raw["period"].strip(),
                "ward": raw["ward"].strip(),
                "category": raw["category"].strip(),
                "budgeted_amount": budgeted,
                "actual_spend": actual,
                "notes": (raw.get("notes") or "").strip(),
            }
            rows.append(row)
            if actual is None:
                nulls.append({
                    "period": row["period"],
                    "ward": row["ward"],
                    "category": row["category"],
                    "notes": row["notes"],
                })
    return rows, nulls


def _prev_period(period: str, growth_type: str) -> str:
    year_str, month_str = period.split("-")
    year, month = int(year_str), int(month_str)
    if growth_type == "MoM":
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
    else:  # YoY
        year -= 1
    return f"{year:04d}-{month:02d}"


def compute_growth(rows: List[dict], ward: str, category: str,
                   growth_type: str) -> List[dict]:
    """Compute per-period growth for one (ward, category) using MoM or YoY."""
    if growth_type not in VALID_GROWTH_TYPES:
        raise ValueError(f"growth_type must be one of {sorted(VALID_GROWTH_TYPES)}; "
                         f"got {growth_type!r}")

    scoped = [r for r in rows if r["ward"] == ward and r["category"] == category]
    if not scoped:
        return []

    by_period: Dict[str, dict] = {r["period"]: r for r in scoped}

    results: List[dict] = []
    for r in scoped:
        period = r["period"]
        actual = r["actual_spend"]
        result = {
            "period": period,
            "ward": r["ward"],
            "category": r["category"],
            "budgeted_amount": r["budgeted_amount"],
            "actual_spend": "" if actual is None else actual,
            "growth_pct": "",
            "formula": "",
            "flag": "",
            "notes": r["notes"],
        }

        if actual is None:
            result["flag"] = "NULL_INPUT"
            result["formula"] = "n/a — actual_spend missing"
            results.append(result)
            continue

        ref_period = _prev_period(period, growth_type)
        ref_row = by_period.get(ref_period)

        if ref_row is None:
            result["flag"] = "NULL_REFERENCE"
            result["formula"] = f"n/a — reference period {ref_period} not in dataset"
        elif ref_row["actual_spend"] is None:
            result["flag"] = "NULL_REFERENCE"
            result["formula"] = f"n/a — reference period {ref_period} actual_spend is null"
        else:
            ref = ref_row["actual_spend"]
            pct = (actual - ref) / ref * 100.0
            result["growth_pct"] = f"{pct:+.1f}%"
            result["formula"] = (
                f"{growth_type}: ({actual} - {ref}) / {ref} * 100 = "
                f"{result['growth_pct']}"
            )

        results.append(result)

    return results


def _refuse(msg: str) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Ward Budget Growth Calculator",
    )
    parser.add_argument("--input",  required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward",   required=True, help="Exact ward name (e.g. 'Ward 1 – Kasba')")
    parser.add_argument("--category", required=True, help="Exact category name (e.g. 'Roads & Pothole Repair')")
    parser.add_argument("--growth-type", required=False, default=None,
                        help="MoM or YoY. Required — refuses if omitted.")
    parser.add_argument("--output", required=True, help="Path to write growth CSV")
    args = parser.parse_args()

    if args.ward.strip().lower() in AGGREGATION_TOKENS:
        _refuse(f"--ward={args.ward!r} requests cross-ward aggregation; not permitted. "
                "Pass an exact ward name from the CSV.")
    if args.category.strip().lower() in AGGREGATION_TOKENS:
        _refuse(f"--category={args.category!r} requests cross-category aggregation; not permitted. "
                "Pass an exact category name from the CSV.")
    if not args.growth_type:
        _refuse("--growth-type is required. Choose MoM or YoY explicitly — "
                "the tool will not guess a formula.")
    if args.growth_type not in VALID_GROWTH_TYPES:
        _refuse(f"--growth-type={args.growth_type!r} not supported. "
                f"Choose one of: {', '.join(sorted(VALID_GROWTH_TYPES))}.")

    rows, nulls = load_dataset(args.input)

    print(f"Loaded {len(rows)} rows. Null actual_spend count: {len(nulls)}")
    for n in nulls:
        print(f"  NULL: {n['period']} · {n['ward']} · {n['category']} "
              f"— {n['notes'] or '(no reason given)'}")

    results = compute_growth(rows, args.ward, args.category, args.growth_type)

    if not results:
        _refuse(f"No rows matched ward={args.ward!r} and category={args.category!r}. "
                "Check spelling — the strings must match the CSV exactly.")

    output_fields = ["period", "ward", "category", "budgeted_amount",
                     "actual_spend", "growth_pct", "formula", "flag", "notes"]

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"Done. {len(results)} rows written to {args.output} "
          f"({args.growth_type} growth for {args.ward} · {args.category}).")


if __name__ == "__main__":
    main()
