# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its structure, and reports every null actual_spend row (with its notes reason) before any computation happens.
    input: >
      file_path (string) — path to the ward budget CSV. Expected columns:
      period (YYYY-MM), ward (string), category (string), budgeted_amount
      (float), actual_spend (float or blank), notes (string).
    output: >
      A structured dataset (one record per row, columns typed as above)
      plus a null_report: a list of {period, ward, category, reason}
      entries — one per row where actual_spend is blank, with reason
      copied verbatim from that row's notes column — and summary counts
      (total_rows, null_count). Nothing downstream may treat a row as
      "clean" until it has passed through this null_report check.
    error_handling: >
      Missing file at file_path -> refuse with a clear "file not found"
      error, no partial load. Missing one or more required columns ->
      refuse and name the missing column(s). Non-numeric value in
      budgeted_amount, or an actual_spend value that is neither numeric
      nor blank -> refuse and identify the offending row (period, ward,
      category). A blank actual_spend whose notes column is also blank
      -> refuse (treated as a data-integrity failure, not a silent null)
      rather than reporting an unexplained gap.

  - name: compute_growth
    description: Computes MoM or YoY growth, period by period, for exactly one ward+category pair, using only the validated output of load_dataset; pure deterministic arithmetic, no cross-ward/cross-category aggregation, no model call.
    input: >
      dataset (the structured output of load_dataset), ward (string,
      must exactly match a value present in the dataset), category
      (string, must exactly match a value present in the dataset),
      growth_type (enum: "MoM" | "YoY").
    output: >
      A list of per-period rows, one per period present for that
      ward+category, each containing: period, actual_spend,
      budgeted_amount, comparison_period (previous month for MoM, same
      month prior year for YoY), comparison_actual_spend, growth_pct
      (a signed percentage, or the literal string "N/A — null data" /
      "N/A — no prior-year data available" when growth cannot be
      computed), formula (the literal arithmetic string with real
      numbers substituted, e.g. "(19.7 - 14.8) / 14.8 * 100 = +33.11%",
      present only when growth_pct is a number), and flag (the notes
      reason, if this row or its comparison row was null).
    error_handling: >
      ward or category not present in the dataset -> refuse and list
      the valid ward/category values instead of guessing a match.
      growth_type missing or not in {MoM, YoY} -> refuse and ask the
      caller to specify one explicitly; never default. Target period's
      actual_spend is null -> do not compute; emit the row with
      growth_pct = "N/A — null data" and flag set to that row's notes
      reason. Comparison/baseline period's actual_spend is null (even
      though the target period itself is not) -> same treatment:
      growth_pct = "N/A — null data", flag surfaces the baseline row's
      notes reason, since the baseline value is required input and is
      missing. YoY requested for a period whose comparison period
      (12 months earlier) does not exist in the dataset at all -> emit
      growth_pct = "N/A — no prior-year data available" rather than
      falling back to MoM or estimating. Caller passes more than one
      ward or category (e.g. a list, "all", or a wildcard) -> refuse;
      this skill only ever accepts a single ward+category pair.
