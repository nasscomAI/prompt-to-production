skills:
  - name: load_dataset
    description: Read the ward-budget CSV, validate schema, and report which rows have null actual_spend before returning.
    input: >
      path (str) to a CSV with header:
        period,ward,category,budgeted_amount,actual_spend,notes
    output: >
      tuple (rows, nulls) where
        rows: list of dicts (all rows, in file order), with actual_spend as
              float or None (blank → None), budgeted_amount as float,
              other fields as str.
        nulls: list of dicts {period, ward, category, notes} — one per row
               with actual_spend is None.
    error_handling: >
      Missing file → raise FileNotFoundError. Missing/reordered columns →
      raise ValueError naming the missing column. Non-numeric budgeted_amount
      → raise ValueError with the offending period/ward/category. Non-numeric
      actual_spend that is not blank → raise ValueError. Never silently
      coerce a bad value to zero.

  - name: compute_growth
    description: For one (ward, category) pair, return a per-period growth table using the specified formula, with nulls flagged not filled.
    input: >
      rows (list of dicts from load_dataset), ward (str, must match rows
      exactly), category (str, must match rows exactly), growth_type (str,
      "MoM" or "YoY").
    output: >
      list of dicts, one per period in file order, with keys:
        period, ward, category, budgeted_amount, actual_spend, growth_pct
          (str "+33.1%" or blank), formula (str showing arithmetic or reason),
        flag (str "" | "NULL_INPUT" | "NULL_REFERENCE"),
        notes (str, copied from source).
    error_handling: >
      Ward or category not found in rows → return [] and let caller emit a
      refusal message. growth_type not in {MoM, YoY} → raise ValueError.
      A period whose actual_spend is None → row emitted with growth_pct=""
      flag=NULL_INPUT, formula="n/a — actual_spend missing". A period whose
      reference (prev month or prev year) is None or missing → row emitted
      with flag=NULL_REFERENCE, formula="n/a — reference period unavailable".
      Never fabricate a reference value.
