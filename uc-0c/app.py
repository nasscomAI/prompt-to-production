"""
UC-0C app.py — Number That Looks Right
Implements load_dataset and compute_growth skills as defined in skills.md.
Agent enforcement rules from agents.md are baked into the computation logic.
Amazon Bedrock (Claude) is used to generate an analytical interpretation of results.
"""
import argparse
import csv
import json
import sys
import boto3

# ---------------------------------------------------------------------------
# AWS Bedrock configuration
# ---------------------------------------------------------------------------
AWS_ACCESS_KEY_ID     = "AKIA5FTZFLDKOFXLXKHQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION            = "us-east-1"
BEDROCK_MODEL_ID      = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

REQUIRED_COLUMNS = {"period", "ward", "category", "budgeted_amount", "actual_spend", "notes"}

# ---------------------------------------------------------------------------
# System prompt for the Bedrock analytical interpretation (from agents.md)
# ---------------------------------------------------------------------------
ANALYSIS_SYSTEM_PROMPT = """You are a budget growth analysis agent. Your operational boundary is to interpret a per-ward per-category growth table produced by a deterministic computation engine.

RULES YOU MUST FOLLOW:
1. Only refer to the data in the table provided — never invent numbers or trends.
2. Never aggregate across wards or categories — the table is already scoped to a single ward and category.
3. Flag and explain any NULL_NOT_COMPUTED rows — do not ignore them.
4. Always state the formula used (MoM or YoY) when describing growth figures.
5. Keep your interpretation factual and traceable to the numbers in the table.

OUTPUT FORMAT:
Provide a 3–5 sentence plain-text interpretation noting:
- The ward and category being analysed
- Notable high/low growth periods with their exact percentages
- Any null periods and the reason given
- The formula used for computation
"""


# ---------------------------------------------------------------------------
# Skill 1: load_dataset
# ---------------------------------------------------------------------------
def load_dataset(file_path: str) -> dict:
    """
    Read ward_budget.csv, validate columns, report null actual_spend rows
    before returning.

    Returns:
        dict with keys:
            "rows"        : list of row dicts (all rows)
            "null_report" : list of {period, ward, category, null_reason}
            "wards"       : sorted list of unique wards
            "categories"  : sorted list of unique categories
    """
    try:
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - fieldnames
            if missing:
                raise ValueError(
                    f"CSV is missing required column(s): {', '.join(sorted(missing))}"
                )
            rows = [dict(r) for r in reader]
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Dataset file not found: '{file_path}'. "
            "Please check the path and try again."
        )

    null_report = []
    for r in rows:
        spend = r.get("actual_spend", "").strip()
        if spend == "" or spend is None:
            null_report.append({
                "period"      : r["period"],
                "ward"        : r["ward"],
                "category"    : r["category"],
                "null_reason" : r.get("notes", "").strip() or "No reason provided"
            })

    wards      = sorted({r["ward"] for r in rows})
    categories = sorted({r["category"] for r in rows})

    return {
        "rows"       : rows,
        "null_report": null_report,
        "wards"      : wards,
        "categories" : categories,
    }


# ---------------------------------------------------------------------------
# Skill 2: compute_growth
# ---------------------------------------------------------------------------
def compute_growth(dataset: dict, ward: str, category: str, growth_type: str) -> list:
    """
    Compute per-period growth for a single ward + category.
    Enforcement:
      - Refuses if growth_type is not 'MoM' or 'YoY'.
      - Never aggregates across wards/categories.
      - Flags null rows as NULL_NOT_COMPUTED with note reason.
      - Shows formula in every output row.

    Returns:
        list of dicts: period, ward, category, actual_spend,
                       growth_pct, formula_used, null_flag
    """
    # Enforcement: refuse if growth_type not specified correctly
    if growth_type not in ("MoM", "YoY"):
        raise ValueError(
            f"Invalid --growth-type '{growth_type}'. "
            "You must specify exactly 'MoM' (month-over-month) or 'YoY' (year-over-year). "
            "This agent never guesses a formula."
        )

    # Validate ward and category exist in dataset
    if ward not in dataset["wards"]:
        raise ValueError(
            f"Ward '{ward}' not found in dataset.\n"
            f"Valid wards: {', '.join(dataset['wards'])}"
        )
    if category not in dataset["categories"]:
        raise ValueError(
            f"Category '{category}' not found in dataset.\n"
            f"Valid categories: {', '.join(dataset['categories'])}"
        )

    # Build null lookup for this ward+category scope
    null_lookup = {
        (n["period"], n["ward"], n["category"]): n["null_reason"]
        for n in dataset["null_report"]
    }

    # Filter rows to the specified ward + category only (enforcement: no aggregation)
    scoped = [
        r for r in dataset["rows"]
        if r["ward"] == ward and r["category"] == category
    ]
    # Sort by period ascending
    scoped.sort(key=lambda r: r["period"])

    # Build a period → spend map (None for nulls)
    period_spend = {}
    for r in scoped:
        spend_str = r.get("actual_spend", "").strip()
        period_spend[r["period"]] = float(spend_str) if spend_str else None

    if growth_type == "MoM":
        formula_label = "((current - previous) / previous) × 100"
    else:
        formula_label = "((current - same_month_prior_year) / same_month_prior_year) × 100"

    output_rows = []
    periods = sorted(period_spend.keys())

    for i, period in enumerate(periods):
        current_spend = period_spend[period]
        null_key      = (period, ward, category)
        null_reason   = null_lookup.get(null_key, "")

        # Null current period
        if current_spend is None:
            output_rows.append({
                "period"       : period,
                "ward"         : ward,
                "category"     : category,
                "actual_spend" : "NULL",
                "growth_pct"   : "NULL_NOT_COMPUTED",
                "formula_used" : formula_label,
                "null_flag"    : null_reason or "actual_spend is null",
            })
            continue

        # Determine comparison period
        if growth_type == "MoM":
            if i == 0:
                # No previous month available
                output_rows.append({
                    "period"       : period,
                    "ward"         : ward,
                    "category"     : category,
                    "actual_spend" : f"{current_spend:.1f}",
                    "growth_pct"   : "N/A (first period)",
                    "formula_used" : formula_label,
                    "null_flag"    : "",
                })
                continue
            prev_period = periods[i - 1]
            prev_spend  = period_spend.get(prev_period)
            prev_null   = null_lookup.get((prev_period, ward, category), "")
        else:  # YoY
            # Same month prior year — periods are YYYY-MM format
            year, month = period.split("-")
            prior_year_period = f"{int(year) - 1}-{month}"
            prev_spend  = period_spend.get(prior_year_period)
            prev_null   = null_lookup.get((prior_year_period, ward, category), "")

        # Null previous period
        if prev_spend is None:
            reason = prev_null or "comparison period actual_spend is null"
            output_rows.append({
                "period"       : period,
                "ward"         : ward,
                "category"     : category,
                "actual_spend" : f"{current_spend:.1f}",
                "growth_pct"   : "NULL_NOT_COMPUTED",
                "formula_used" : formula_label,
                "null_flag"    : f"Comparison period is null: {reason}",
            })
            continue

        if prev_spend == 0:
            output_rows.append({
                "period"       : period,
                "ward"         : ward,
                "category"     : category,
                "actual_spend" : f"{current_spend:.1f}",
                "growth_pct"   : "UNDEFINED (division by zero — previous spend was 0)",
                "formula_used" : formula_label,
                "null_flag"    : "",
            })
            continue

        growth = ((current_spend - prev_spend) / prev_spend) * 100
        output_rows.append({
            "period"       : period,
            "ward"         : ward,
            "category"     : category,
            "actual_spend" : f"{current_spend:.1f}",
            "growth_pct"   : f"{growth:+.1f}%",
            "formula_used" : formula_label,
            "null_flag"    : "",
        })

    return output_rows


# ---------------------------------------------------------------------------
# Bedrock analytical interpretation
# ---------------------------------------------------------------------------
def interpret_with_bedrock(growth_rows: list, ward: str, category: str,
                           growth_type: str, null_report: list) -> str:
    """
    Call Amazon Bedrock to generate a plain-text analytical interpretation
    of the computed growth table.
    Falls back to a local summary string if the API call fails.
    """
    table_text = "\n".join(
        f"{r['period']} | spend={r['actual_spend']} | growth={r['growth_pct']}"
        + (f" | NULL FLAG: {r['null_flag']}" if r["null_flag"] else "")
        for r in growth_rows
    )

    scoped_nulls = [
        n for n in null_report
        if n["ward"] == ward and n["category"] == category
    ]
    null_summary = "\n".join(
        f"  {n['period']}: {n['null_reason']}" for n in scoped_nulls
    ) or "  None"

    user_message = (
        f"Analyse the following {growth_type} growth table for:\n"
        f"Ward: {ward}\nCategory: {category}\nFormula: {growth_type}\n\n"
        f"GROWTH TABLE:\n{table_text}\n\n"
        f"NULL ROWS IN THIS SCOPE:\n{null_summary}"
    )

    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens"       : 512,
            "system"           : ANALYSIS_SYSTEM_PROMPT,
            "messages"         : [{"role": "user", "content": user_message}]
        })
        response = client.invoke_model(
            modelId     = BEDROCK_MODEL_ID,
            contentType = "application/json",
            accept      = "application/json",
            body        = body,
        )
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]

    except Exception as e:
        print(f"WARNING: Bedrock interpretation unavailable: {e}")
        non_null = [r for r in growth_rows if r["growth_pct"] not in ("NULL_NOT_COMPUTED", "N/A (first period)") and "UNDEFINED" not in r["growth_pct"]]
        if non_null:
            values = [float(r["growth_pct"].replace("%", "").replace("+", "")) for r in non_null]
            avg    = sum(values) / len(values)
            return (
                f"[Local fallback] {growth_type} growth for {ward} / {category}: "
                f"{len(growth_rows)} periods computed. "
                f"Average growth: {avg:+.1f}%. "
                f"Null periods: {len(scoped_nulls)}."
            )
        return f"[Local fallback] {growth_type} growth table generated. {len(scoped_nulls)} null period(s) flagged."


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="UC-0C Budget Growth Analyser")
    parser.add_argument("--input",       required=True,  help="Path to ward_budget.csv")
    parser.add_argument("--ward",        required=True,  help='Ward name, e.g. "Ward 1 – Kasba"')
    parser.add_argument("--category",    required=True,  help='Category, e.g. "Roads & Pothole Repair"')
    parser.add_argument("--growth-type", required=True,  dest="growth_type",
                        help="Growth formula: MoM (month-over-month) or YoY (year-over-year)")
    parser.add_argument("--output",      required=True,  help="Path to write growth_output.csv")
    args = parser.parse_args()

    # Enforce growth-type explicitly — never guess (agents.md enforcement rule 4)
    if args.growth_type not in ("MoM", "YoY"):
        print(
            f"ERROR: --growth-type must be exactly 'MoM' or 'YoY'. "
            f"Got: '{args.growth_type}'. This agent never defaults or guesses a formula.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Skill 1: load_dataset
    print(f"Loading dataset: {args.input}")
    dataset = load_dataset(args.input)
    print(f"  Loaded {len(dataset['rows'])} rows across "
          f"{len(dataset['wards'])} wards, {len(dataset['categories'])} categories.")

    # Report all nulls before computing (agents.md enforcement rule 2)
    if dataset["null_report"]:
        print(f"\n  [!] {len(dataset['null_report'])} NULL actual_spend row(s) found in full dataset:")
        for n in dataset["null_report"]:
            print(f"     {n['period']} | {n['ward']} | {n['category']} -> {n['null_reason']}")
    else:
        print("  [OK] No null actual_spend rows found.")

    # Skill 2: compute_growth
    print(f"\nComputing {args.growth_type} growth for:")
    print(f"  Ward    : {args.ward}")
    print(f"  Category: {args.category}")
    growth_rows = compute_growth(dataset, args.ward, args.category, args.growth_type)

    # Write output CSV
    fieldnames = ["period", "ward", "category", "actual_spend", "growth_pct", "formula_used", "null_flag"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(growth_rows)
    print(f"\nGrowth table written to: {args.output}")

    # Bedrock interpretation
    print("\nCalling Amazon Bedrock for analytical interpretation...")
    interpretation = interpret_with_bedrock(
        growth_rows, args.ward, args.category, args.growth_type, dataset["null_report"]
    )
    print("\n─── AGENT INTERPRETATION ───")
    print(interpretation)
    print("────────────────────────────")
    print("\nDone.")


if __name__ == "__main__":
    main()
