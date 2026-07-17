# skills.md

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports the null actual_spend rows (with their notes reason) before any computation happens.
    input: >
      input_path (str) — path to ward_budget.csv with columns period, ward,
      category, budgeted_amount, actual_spend, notes.
    output: >
      A list of row dicts (one per CSV row, all raw string values). Before
      returning, prints the total row count and, for every row with a blank
      actual_spend, its period/ward/category and the notes-column reason.
    error_handling: >
      If a required column is missing from the CSV header, raise an error
      immediately — never silently proceed with a partial schema.

  - name: compute_growth
    description: Computes per-period growth (MoM or YoY) for exactly one ward + category, showing the formula for every computed row and flagging rows that cannot be computed instead of guessing.
    input: >
      rows (list, from load_dataset), ward (str, exact match), category (str,
      exact match), growth_type ("MoM" or "YoY" — never defaulted).
    output: >
      A list of dicts, one per period for that ward/category, each with:
      period, actual_spend, growth_pct, formula (the exact arithmetic used),
      and flag (set instead of growth_pct/formula when the value or its
      comparison period is unavailable).
    error_handling: >
      If actual_spend for the period is null, or the prior period needed for
      the comparison is null or absent from the dataset, the row is flagged
      NOT_COMPUTED with the specific reason (citing the notes column where
      applicable) instead of computing a number. No ward/category aggregation
      is ever performed — the caller must pass exactly one of each.
