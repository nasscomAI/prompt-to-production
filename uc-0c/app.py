"""
UC-0C — Budget Growth Analyst (Number That Looks Right)

Built from the RICE contract in agents.md and the skill specs in skills.md.
Deterministic, stdlib-only: no network/LLM calls.

The failure modes this UC targets — wrong aggregation level, silent null
handling, and silent formula choice — are all prevented BY DESIGN here:
  - the tool only ever operates on ONE ward + ONE category (no aggregation),
    and refuses explicitly if asked to aggregate                 (aggregation guard)
  - null actual_spend is loaded as None, reported up front, and flagged per row
    with its notes reason instead of being computed or skipped   (null guard)
  - --growth-type is NOT defaulted; if it is missing or invalid the tool refuses
    and asks rather than guessing MoM vs YoY                      (formula guard)
  - every computed row prints the exact formula used             (transparency)

Verified against the README reference values:
  Ward 1 – Kasba / Roads & Pothole Repair : 2024-07 = +33.1%, 2024-10 = −34.8%.
"""
import argparse
import csv
import sys

# Windows consoles often default to cp1252, which cannot print the report's
# dashes/arrows. Make stdout UTF-8 so the report renders on every platform.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

EXPECTED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
VALID_GROWTH_TYPES = ("MoM", "YoY")
AGGREGATE_TOKENS = {"all", "all wards", "all categories", "*", "total", "aggregate", "everything"}

OUTPUT_FIELDS = [
    "period", "ward", "category", "growth_type", "actual_spend",
    "prev_period", "prev_actual_spend", "growth_pct", "formula", "flag",
]


class RefusalError(Exception):
    """Raised when the agent must refuse rather than guess (see agents.md)."""


def _norm(value: str) -> str:
    """Normalise for comparison: unify dash variants, collapse space, lowercase."""
    if value is None:
        return ""
    v = value.replace("–", "-").replace("—", "-")  # en/em dash -> hyphen
    return " ".join(v.split()).strip().lower()


def load_dataset(input_path: str) -> list:
    """
    Read the ward budget CSV, validate columns, and report null actual_spend rows.
    Returns a list of row dicts with actual_spend as float or None.
    Fails loudly on a missing file or missing column.
    """
    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        missing = [c for c in EXPECTED_COLUMNS if c not in header]
        if missing:
            raise ValueError(f"Input CSV is missing required column(s): {', '.join(missing)}")

        rows = []
        for raw in reader:
            spend_raw = (raw.get("actual_spend") or "").strip()
            rows.append({
                "period": (raw.get("period") or "").strip(),
                "ward": (raw.get("ward") or "").strip(),
                "category": (raw.get("category") or "").strip(),
                "budgeted_amount": (raw.get("budgeted_amount") or "").strip(),
                "actual_spend": float(spend_raw) if spend_raw else None,
                "notes": (raw.get("notes") or "").strip(),
            })

    nulls = [r for r in rows if r["actual_spend"] is None]
    print(f"Loaded {len(rows)} row(s) from {input_path}.")
    print(f"Null actual_spend rows: {len(nulls)} (these will be FLAGGED, never computed):")
    for r in nulls:
        reason = r["notes"] or "(no reason given in notes)"
        print(f"  - {r['period']} · {r['ward']} · {r['category']} → {reason}")
    return rows


def _resolve_series(rows, ward, category):
    """Return the rows for exactly one ward+category, or refuse."""
    if _norm(ward) in AGGREGATE_TOKENS or _norm(category) in AGGREGATE_TOKENS:
        raise RefusalError(
            "Refusing to aggregate. This tool reports growth for ONE ward and ONE "
            "category at a time; cross-ward / cross-category totals are not supported "
            "(see agents.md enforcement rule 1)."
        )

    wards = sorted({r["ward"] for r in rows})
    cats = sorted({r["category"] for r in rows})
    ward_match = [w for w in wards if _norm(w) == _norm(ward)]
    cat_match = [c for c in cats if _norm(c) == _norm(category)]

    if not ward_match:
        raise RefusalError(f"Ward '{ward}' not found. Available wards: {wards}")
    if not cat_match:
        raise RefusalError(f"Category '{category}' not found. Available categories: {cats}")

    series = [r for r in rows if r["ward"] == ward_match[0] and r["category"] == cat_match[0]]
    series.sort(key=lambda r: r["period"])
    return ward_match[0], cat_match[0], series


def compute_growth(rows, ward, category, growth_type):
    """
    Compute per-period growth for ONE ward+category. Returns a per-period table.
    Refuses on unspecified/invalid growth_type or on aggregation requests.
    """
    if growth_type not in VALID_GROWTH_TYPES:
        raise RefusalError(
            f"Refusing to guess a growth measure. --growth-type must be one of "
            f"{VALID_GROWTH_TYPES}; got {growth_type!r}. Please specify which to use "
            "(see agents.md enforcement rule 4)."
        )

    ward, category, series = _resolve_series(rows, ward, category)
    by_period = {r["period"]: r for r in series}
    table = []

    for i, row in enumerate(series):
        period = row["period"]
        cur = row["actual_spend"]

        if growth_type == "MoM":
            prev_row = series[i - 1] if i > 0 else None
        else:  # YoY: same month, previous year
            year, month = period.split("-")
            prev_key = f"{int(year) - 1}-{month}"
            prev_row = by_period.get(prev_key)

        prev_period = prev_row["period"] if prev_row else ""
        prev = prev_row["actual_spend"] if prev_row else None

        out = {
            "period": period, "ward": ward, "category": category,
            "growth_type": growth_type, "actual_spend": "" if cur is None else cur,
            "prev_period": prev_period, "prev_actual_spend": "" if prev is None else prev,
            "growth_pct": "", "formula": "", "flag": "",
        }

        # --- Flag conditions (never compute through a null / missing base) ---
        if cur is None:
            out["flag"] = f"NULL_CURRENT: {row['notes'] or 'actual_spend missing'}"
            out["formula"] = "not computed — current actual_spend is null"
        elif prev_row is None:
            out["flag"] = "NO_PRIOR_PERIOD" if growth_type == "MoM" else "NO_PRIOR_YEAR_DATA"
            out["formula"] = "not computed — no prior period to compare against"
        elif prev is None:
            out["flag"] = f"NULL_PREVIOUS: prior period {prev_period} actual_spend is null"
            out["formula"] = "not computed — prior actual_spend is null"
        else:
            growth = (cur - prev) / prev * 100
            out["growth_pct"] = f"{growth:+.1f}%"
            out["formula"] = f"{growth_type} = ({cur} - {prev}) / {prev} × 100 = {growth:+.1f}%"

        table.append(out)

    return table


def write_output(table, output_path):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(table)


def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyst")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", required=True, help="Single ward, e.g. 'Ward 1 – Kasba'")
    parser.add_argument("--category", required=True, help="Single category, e.g. 'Roads & Pothole Repair'")
    # NOT defaulted on purpose: an unspecified growth type must be refused, not guessed.
    parser.add_argument("--growth-type", default=None, help="MoM or YoY (required — no default)")
    parser.add_argument("--output", required=True, help="Path to write the per-period growth CSV")
    args = parser.parse_args()

    try:
        rows = load_dataset(args.input)
        table = compute_growth(rows, args.ward, args.category, args.growth_type)
    except RefusalError as r:
        print(f"\nREFUSED: {r}")
        sys.exit(2)

    write_output(table, args.output)
    computed = sum(1 for t in table if t["growth_pct"])
    flagged = sum(1 for t in table if t["flag"])
    print(f"\nWrote {len(table)} row(s) to {args.output} "
          f"({computed} computed, {flagged} flagged) for {args.ward} / {args.category} [{args.growth_type}].")


if __name__ == "__main__":
    main()
