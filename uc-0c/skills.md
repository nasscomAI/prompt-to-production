# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, identifies and reports all null actual_spend rows with their notes reasons before returning the dataset for computation.
    input: >
      A single file path as string:
        - file_path — path to the budget CSV (e.g. ../data/budget/ward_budget.csv)
      Required columns: period · ward · category · actual_spend · notes
    output: >
      A dict containing:
        - data (list of dicts) — all 300 rows, each with all original columns
        - null_rows (list of dicts) — the rows where actual_spend is blank/null,
          each containing: period · ward · category · null_reason (from notes column)
        - null_count (int) — total count of null actual_spend rows (expected: 5)
        - summary (string) — human-readable report of null rows printed to stdout
          before any computation proceeds
      The budgeted_amount column is loaded but must not be used in growth calculations
      unless explicitly requested.
    error_handling: >
      If file_path does not exist: raise FileNotFoundError with the path.
      If any required column is missing: raise ValueError naming the missing column(s).
      If null_count differs from 5: log a warning "WARNING: Expected 5 null rows,
      found {null_count}" — do not abort, but surface the discrepancy.

  - name: compute_growth
    description: Calculates per-period MoM or YoY actual_spend growth for a single specified ward and category, showing the formula used in every output row and flagging null rows rather than computing them.
    input: >
      Four arguments:
        - data (list of dicts) — the full dataset from load_dataset
        - ward (string) — exact ward name (e.g. "Ward 1 – Kasba")
        - category (string) — exact category name (e.g. "Roads & Pothole Repair")
        - growth_type (string) — must be exactly "MoM" or "YoY"; if not provided
          or any other value: refuse immediately (see error_handling)
    output: >
      A list of dicts written to growth_output.csv, one row per period, each containing:
        - period (YYYY-MM)
        - actual_spend (float in ₹ lakh, or "NULL" with null_reason if flagged)
        - growth (string — e.g. "+33.1%" or "NULL_FLAGGED")
        - formula (string — e.g. "(19.7 − 14.8) / 14.8 × 100 = +33.1%", or
          "NULL — not computed: {null_reason}" for flagged rows)
      Reference: Ward 1–Kasba · Roads · 2024-07 must = +33.1%; 2024-10 must = −34.8%.
    error_handling: >
      If growth_type is missing or not "MoM"/"YoY": print exactly —
        "Growth type not specified. Please provide --growth-type MoM or --growth-type YoY."
      and exit without computing anything — never default silently.
      If ward or category does not exist in the dataset: raise ValueError naming the
      unrecognised value.
      If aggregation across all wards is requested: print exactly —
        "Cross-ward aggregation is not supported. Please specify a single ward."
      and exit.
