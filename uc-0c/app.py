"""
UC-0C app.py - Ward budget growth calculator.

Implements the two skills in skills.md under the enforcement rules in agents.md:
  - load_dataset:   read CSV, validate columns, report nulls BEFORE returning
  - compute_growth: one ward + one category + explicit growth type -> per-period
                    table with the formula shown on every row

Run:
  python app.py --input ../data/budget/ward_budget.csv \
    --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair" \
    --growth-type MoM --output growth_output.csv

Exit codes: 0 = success, 1 = dataset/file error, 2 = refusal (bad or missing scope/formula).
"""
import argparse
import csv
import re
import sys

REQUIRED_COLUMNS = ["period", "ward", "category", "budgeted_amount", "actual_spend", "notes"]
GROWTH_LAG_MONTHS = {"MoM": 1, "YoY": 12}
AGGREGATE_TOKENS = {"all", "any", "*", "every", "total", "overall", "all wards",
                    "all categories", "every ward", "every category"}
PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
OUTPUT_COLUMNS = ["ward", "category", "period", "actual_spend", "prior_period",
                  "prior_actual_spend", "growth_type", "formula", "growth_pct",
                  "flag", "note"]


class RefusalError(Exception):
    """The request must be refused rather than guessed at."""


class DatasetError(Exception):
    """The input file cannot be trusted or read."""


# --------------------------------------------------------------------------- helpers
def _norm(text):
    """Case-, whitespace- and dash-insensitive key for matching ward/category names."""
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", text or "")
    return re.sub(r"\s+", " ", text).strip().casefold()


def _shift_period(period, months_back):
    year, month = int(period[:4]), int(period[5:7])
    idx = year * 12 + (month - 1) - months_back
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def _parse_amount(raw):
    """Return (value, problem). Blank -> (None, None). Non-numeric -> (None, message)."""
    raw = (raw or "").strip()
    if raw == "":
        return None, None
    try:
        return float(raw), None
    except ValueError:
        return None, f"non-numeric value '{raw}'"


def _null_reason(row):
    reason = row["notes"] or "no reason given in notes column"
    if row["parse_issue"]:
        reason = f"{row['parse_issue']} ({reason})"
    return reason


# --------------------------------------------------------------------------- skill 1
def load_dataset(path):
    """Skill: load_dataset. Prints the null report before returning."""
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing:
                raise DatasetError(
                    f"Input file is missing required column(s): {', '.join(missing)}. "
                    f"Expected: {', '.join(REQUIRED_COLUMNS)}."
                )
            raw_rows = list(reader)
    except FileNotFoundError:
        raise DatasetError(f"Input file not found: {path}")
    except OSError as exc:
        raise DatasetError(f"Cannot read input file {path}: {exc}")

    rows, bad_rows = [], []
    for line_no, raw in enumerate(raw_rows, start=2):  # line 1 is the header
        period = (raw.get("period") or "").strip()
        if not PERIOD_RE.match(period):
            bad_rows.append({"line": line_no, "period": period})
            continue
        budgeted, _ = _parse_amount(raw.get("budgeted_amount"))
        actual, issue = _parse_amount(raw.get("actual_spend"))
        rows.append({
            "line": line_no,
            "period": period,
            "ward": (raw.get("ward") or "").strip(),
            "category": (raw.get("category") or "").strip(),
            "budgeted": budgeted,
            "actual": actual,
            "notes": (raw.get("notes") or "").strip(),
            "parse_issue": issue,
        })

    null_rows = [r for r in rows if r["actual"] is None]

    # ---- null report: printed BEFORE the dataset is returned ----
    print(f"[load_dataset] {len(rows)} rows loaded from {path}")
    print(f"[load_dataset] NULL actual_spend rows: {len(null_rows)}")
    for r in null_rows:
        print(f"    - {r['period']} | {r['ward']} | {r['category']} | reason: {_null_reason(r)}")
    if bad_rows:
        print(f"[load_dataset] WARNING: {len(bad_rows)} row(s) excluded for malformed period:")
        for b in bad_rows:
            print(f"    - line {b['line']}: period = '{b['period']}'")
    print()

    return {"rows": rows, "null_rows": null_rows, "bad_rows": bad_rows}


# --------------------------------------------------------------------------- skill 2
def validate_request(ward, category, growth_type):
    """Refuse before touching data when scope or formula is missing or an aggregation."""
    if not growth_type:
        raise RefusalError(
            "--growth-type was not specified. I will not guess a formula. "
            "Please choose one: MoM (month-over-month) or YoY (year-over-year)."
        )
    if growth_type not in GROWTH_LAG_MONTHS:
        raise RefusalError(
            f"--growth-type '{growth_type}' is not supported. Use exactly MoM or YoY."
        )
    for label, value in (("--ward", ward), ("--category", category)):
        if not value or not value.strip():
            raise RefusalError(
                f"{label} was not specified. Growth is computed for ONE ward and ONE "
                "category at a time; aggregating across wards or categories is not permitted."
            )
        if _norm(value) in AGGREGATE_TOKENS:
            raise RefusalError(
                f"{label} '{value}' asks for an aggregation across the dataset. "
                "Cross-ward / cross-category aggregation is not permitted. "
                "Name exactly one ward and one category."
            )


def compute_growth(dataset, ward, category, growth_type):
    """Skill: compute_growth. Returns one output row per period for ward + category."""
    validate_request(ward, category, growth_type)
    lag = GROWTH_LAG_MONTHS[growth_type]

    rows = dataset["rows"]
    wards = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})

    ward_match = [w for w in wards if _norm(w) == _norm(ward)]
    if not ward_match:
        raise RefusalError(
            f"Ward '{ward}' not found in the dataset. Valid wards: " + "; ".join(wards)
        )
    cat_match = [c for c in categories if _norm(c) == _norm(category)]
    if not cat_match:
        raise RefusalError(
            f"Category '{category}' not found in the dataset. Valid categories: "
            + "; ".join(categories)
        )
    ward_name, cat_name = ward_match[0], cat_match[0]

    scoped = [r for r in rows if r["ward"] == ward_name and r["category"] == cat_name]
    if not scoped:
        raise RefusalError(f"No rows found for {ward_name} / {cat_name}.")

    by_period = {}
    for r in scoped:
        if r["period"] in by_period:
            raise RefusalError(
                f"Duplicate rows for {ward_name} / {cat_name} in {r['period']} "
                "(lines "
                f"{by_period[r['period']]['line']} and {r['line']}). "
                "I will not guess which one is correct."
            )
        by_period[r["period"]] = r

    out = []
    for period in sorted(by_period):
        cur = by_period[period]
        prior_period = _shift_period(period, lag)
        prior = by_period.get(prior_period)

        result = {
            "ward": ward_name,
            "category": cat_name,
            "period": period,
            "actual_spend": "" if cur["actual"] is None else cur["actual"],
            "prior_period": prior_period,
            "prior_actual_spend": "" if (prior is None or prior["actual"] is None) else prior["actual"],
            "growth_type": growth_type,
            "formula": "",
            "growth_pct": "",
            "flag": "",
            "note": "",
        }

        if cur["actual"] is None:
            result["flag"] = "NULL_ACTUAL_SPEND"
            result["note"] = _null_reason(cur)
            result["formula"] = f"NOT COMPUTED - actual_spend for {period} is null"
        elif prior is None:
            result["flag"] = "NO_PRIOR_PERIOD"
            result["note"] = f"No {prior_period} row in the dataset to compare against"
            result["formula"] = f"NOT COMPUTED - no {prior_period} data for {growth_type}"
        elif prior["actual"] is None:
            result["flag"] = "NULL_PRIOR_SPEND"
            result["note"] = f"{prior_period} actual_spend is null: {_null_reason(prior)}"
            result["formula"] = f"NOT COMPUTED - prior period {prior_period} actual_spend is null"
        elif prior["actual"] == 0:
            result["flag"] = "ZERO_BASE"
            result["note"] = f"{prior_period} actual_spend is 0; growth is undefined"
            result["formula"] = f"NOT COMPUTED - division by zero (prior {prior_period} = 0)"
        else:
            pct = (cur["actual"] - prior["actual"]) / prior["actual"] * 100
            result["growth_pct"] = f"{pct:.1f}"
            result["formula"] = (
                f"{growth_type} = (actual[{period}] - actual[{prior_period}]) / actual[{prior_period}] * 100 "
                f"= ({cur['actual']} - {prior['actual']}) / {prior['actual']} * 100 = {pct:+.1f}%"
            )
        out.append(result)
    return out


# --------------------------------------------------------------------------- output
def write_output(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def print_table(rows):
    print(f"{'period':<9}{'actual':>8}{'growth %':>10}  {'flag':<18} formula / note")
    for r in rows:
        growth = r["growth_pct"] if r["growth_pct"] != "" else "-"
        actual = r["actual_spend"] if r["actual_spend"] != "" else "NULL"
        tail = r["formula"] if not r["flag"] else f"{r['formula']}  [{r['note']}]"
        print(f"{r['period']:<9}{str(actual):>8}{growth:>10}  {r['flag']:<18} {tail}")


def main():
    parser = argparse.ArgumentParser(description="UC-0C per-ward per-category growth calculator")
    parser.add_argument("--input", required=True, help="Path to ward_budget.csv")
    parser.add_argument("--ward", help='Exactly one ward, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category", help='Exactly one category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", dest="growth_type",
                        help="MoM or YoY (required - never guessed)")
    parser.add_argument("--output", required=True, help="Path to write growth_output.csv")
    args = parser.parse_args()

    try:
        # Refuse bad scope/formula up front, before any file is read or written.
        validate_request(args.ward, args.category, args.growth_type)
        dataset = load_dataset(args.input)           # null report printed here
        rows = compute_growth(dataset, args.ward, args.category, args.growth_type)
    except RefusalError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    except DatasetError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    write_output(rows, args.output)
    print(f"{rows[0]['ward']} | {rows[0]['category']} | {args.growth_type}")
    print_table(rows)

    flagged = [r for r in rows if r["flag"]]
    computed = len(rows) - len(flagged)
    print(f"\n{computed} period(s) computed, {len(flagged)} flagged (not computed).")
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
