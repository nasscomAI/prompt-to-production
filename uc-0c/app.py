"""
UC-0C — Number That Looks Right
Per-ward, per-category growth calculator for ward_budget.csv.
It refuses all-ward / all-category aggregation, refuses to guess --growth-type,
flags every null actual_spend (with the reason from the notes column) instead of
computing over it, and shows the formula used in every output row.
"""
import argparse
import csv
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
NULL_TOKENS = {"", "null", "na", "n/a", "nan", "none"}
AGGREGATE_WORDS = {"all", "any", "*", "every", "total", "overall", "combined"}
GROWTH_TYPES = ("MoM", "YoY")


class Refusal(Exception):
    """Raised when the request must be refused rather than guessed."""


def _norm(s: str) -> str:
    return " ".join(s.replace("\u2013", "-").replace("\u2014", "-").lower().split())


def _to_float(value: str):
    """Return (number or None, is_valid). Blank / NULL tokens -> (None, True)."""
    v = (value or "").strip()
    if v.lower() in NULL_TOKENS:
        return None, True
    try:
        return float(v), True
    except ValueError:
        return None, False


# ---------------------------------------------------------------- skill 1
def load_dataset(path: str) -> tuple:
    """Read the CSV, validate columns, report nulls BEFORE returning.
    Returns (rows, null_rows)."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("Input file is missing required columns: " + ", ".join(missing))
        rows = list(reader)

    null_rows = []
    for r in rows:
        val, ok = _to_float(r["actual_spend"])
        r["_actual"] = val
        r["_valid"] = ok
        if val is None:
            reason = (r.get("notes") or "").strip() or ("non-numeric value '%s'" % r["actual_spend"] if not ok else "no reason given")
            null_rows.append({"period": r["period"], "ward": r["ward"],
                              "category": r["category"], "reason": reason})

    print(f"Loaded {len(rows)} rows. Null/invalid actual_spend rows: {len(null_rows)}")
    for n in null_rows:
        print(f"  NULL: {n['period']} | {n['ward']} | {n['category']} | reason: {n['reason']}")
    return rows, null_rows


# ---------------------------------------------------------------- skill 2
def _resolve(value: str, options: list, label: str) -> str:
    if value is None or not value.strip():
        raise Refusal(f"--{label} was not specified. Refusing to aggregate across all {label}s. "
                      f"Choose one of: {'; '.join(options)}")
    if _norm(value) in AGGREGATE_WORDS:
        raise Refusal(f"Aggregation across all {label}s is not allowed. Choose one {label}: {'; '.join(options)}")
    for opt in options:
        if _norm(opt) == _norm(value):
            return opt
    raise Refusal(f"Unknown {label} '{value}'. Valid values: {'; '.join(options)}")


def compute_growth(rows: list, ward: str, category: str, growth_type: str) -> list:
    """Return a per-period table for ONE ward and ONE category, formula shown per row."""
    if not growth_type:
        raise Refusal("--growth-type was not specified. Refusing to guess. Please choose MoM or YoY.")
    gt = {g.lower(): g for g in GROWTH_TYPES}.get(growth_type.strip().lower())
    if gt is None:
        raise Refusal(f"Unknown growth type '{growth_type}'. Please choose MoM or YoY.")

    ward = _resolve(ward, sorted({r["ward"] for r in rows}), "ward")
    category = _resolve(category, sorted({r["category"] for r in rows}), "category")

    series = sorted((r for r in rows if r["ward"] == ward and r["category"] == category),
                    key=lambda r: r["period"])
    if not series:
        raise Refusal(f"No rows found for {ward} / {category}.")

    by_period = {r["period"]: r for r in series}
    out = []
    for i, r in enumerate(series):
        cur = r["_actual"]
        row = {"ward": ward, "category": category, "period": r["period"],
               "actual_spend": "" if cur is None else r["actual_spend"].strip(),
               "growth_type": gt, "growth_pct": "", "formula": "", "flag": ""}

        # Which earlier period do we compare with?
        if gt == "MoM":
            prev = series[i - 1] if i > 0 else None
            basis = "previous month"
            formula = "MoM = (current - previous) / previous * 100"
        else:
            y, m = r["period"].split("-")
            prev = by_period.get(f"{int(y) - 1}-{m}")
            basis = "same month last year"
            formula = "YoY = (current - same month last year) / same month last year * 100"
        row["formula"] = formula

        if cur is None:
            reason = (r.get("notes") or "").strip() or "no reason given"
            row["flag"] = f"NULL actual_spend - not computed. Reason: {reason}"
        elif prev is None:
            row["flag"] = f"No {basis} in the dataset - growth not computed"
        elif prev["_actual"] is None:
            reason = (prev.get("notes") or "").strip() or "no reason given"
            row["flag"] = f"{basis.capitalize()} ({prev['period']}) is NULL - not computed. Reason: {reason}"
        elif prev["_actual"] == 0:
            row["flag"] = f"{basis.capitalize()} ({prev['period']}) is 0 - division by zero, not computed"
        else:
            p = prev["_actual"]
            pct = (cur - p) / p * 100
            row["growth_pct"] = f"{pct:+.1f}%"
            row["formula"] = f"{formula} = ({cur} - {p}) / {p} * 100"
        out.append(row)
    return out


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="UC-0C Ward Budget Growth")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help='Exactly one ward, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", help='Exactly one category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type", help="MoM or YoY (required, never guessed)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    rows, _ = load_dataset(args.input)          # nulls are reported before any calculation
    try:
        table = compute_growth(rows, args.ward, args.category, args.growth_type)
    except Refusal as e:
        print("REFUSED: " + str(e))
        sys.exit(2)

    fields = ["ward", "category", "period", "actual_spend", "growth_type", "growth_pct", "formula", "flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(table)
    flagged = sum(1 for r in table if r["flag"])
    print(f"Done. {len(table)} rows written to {args.output} ({flagged} flagged).")


if __name__ == "__main__":
    main()