skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns and values, and reports every null actual_spend row before returning the data.
    input: >
      path (str) to a UTF-8 CSV with header period,ward,category,budgeted_amount,
      actual_spend,notes, where period is YYYY-MM, budgeted_amount is a float and
      actual_spend is a float or blank.
    output: >
      tuple (rows, null_rows): rows is a list of dicts with period (str),
      ward (str), category (str), budgeted_amount (float), actual_spend (float or
      None), notes (str); null_rows is the list of rows where actual_spend is None,
      each carrying its notes as the null reason. A null report (count + each
      period/ward/category/reason) is printed before returning.
    error_handling: >
      File missing or any required column missing -> stop with a clear error. A
      non-numeric actual_spend or budgeted_amount, or a malformed period -> stop and
      name the offending line (never coerce to 0). Blank actual_spend -> kept as None
      and reported in the null report with its notes reason, never dropped or
      zero-filled (silent null handling).

  - name: compute_growth
    description: Takes one ward, one category and an explicit growth type and returns a per-period growth table with the formula shown on every row.
    input: >
      rows (list of dicts from load_dataset), ward (str, exact ward name),
      category (str, exact category name), growth_type (str, MoM or YoY).
    output: >
      list of dicts, one per period in ascending order, with keys period, ward,
      category, actual_spend, previous_period, previous_spend, growth_pct (str like
      "+33.1" or blank), formula (str with numbers substituted), flag (str, blank or a
      reason code with explanation).
    error_handling: >
      growth_type missing or not MoM/YoY -> refuse and ask which to use (formula
      assumption). ward or category is 'all', '*', 'any', blank, or a list -> refuse:
      cross-ward/category aggregation is not allowed (wrong aggregation level).
      Unknown ward or category -> refuse and list valid values. Current or previous
      actual_spend null -> growth_pct blank, flag NULL_CURRENT or NULL_PREVIOUS with
      the notes reason. No comparable prior period (first month for MoM, any 2024
      month for YoY since the data has no 2023) -> growth_pct blank, flag NO_PRIOR_PERIOD.
