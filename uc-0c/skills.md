# skills.md

skills:
  - name: load_dataset
    description: Reads the input CSV, validates its schema, and reports every null actual_spend row with its notes reason before any computation happens.
    input: >
      File path to a UTF-8 CSV (str) with required columns
      period (YYYY-MM), ward (str), category (str),
      budgeted_amount (float), actual_spend (float or blank), notes (str).
    output: >
      A dataset report object containing:
      - rows: list of all 300 parsed records
      - wards: sorted list of distinct ward names exactly as they appear in the CSV
      - categories: sorted list of distinct category names exactly as they appear in the CSV
      - periods: sorted list of distinct period values (expected 2024-01 .. 2024-12)
      - nulls: list of {period, ward, category, notes} for every blank actual_spend,
        with notes quoted verbatim
    error_handling: >
      If the file is missing or unreadable → fail with the path attempted.
      If any required column is absent → fail listing missing vs expected columns.
      Never impute, drop, or zero-fill null rows; they are reported, not repaired.

  - name: compute_growth
    description: Computes period-over-period growth of actual_spend for exactly one ward and one category and returns a per-period table that shows the formula used on every row.
    input: >
      - ward: str, must exactly match a value from load_dataset().wards
        (e.g. "Ward 1 – Kasba")
      - category: str, must exactly match a value from load_dataset().categories
        (e.g. "Roads & Pothole Repair")
      - growth_type: "MoM" | "YoY" — REQUIRED; MoM = (curr − prev) / prev × 100
        using the immediately preceding month; YoY compares to same month of prior
        year. No default exists.
    output: >
      A table with one row per period for the selected ward + category:
      period, actual_spend (or NULL), formula_used (string shown verbatim per row),
      growth_pct (number or empty when not computable). Null rows carry a flag with
      the notes-column reason quoted verbatim and growth left uncomputed.
    error_handling: >
      - growth_type missing/None → REFUSE and ask whether MoM or YoY is intended;
        never silently default.
      - ward or category not an exact match → REFUSE and print the valid options
        from load_dataset(); never fuzzy-match or guess the closest name.
      - Request spanning multiple wards or categories, or an all-ward/all-category
        aggregate → REFUSE; this agent computes one ward × one category only.
      - First period (no predecessor) or null neighbour value → growth_pct left
        empty with the reason stated in the row; NULL never treated as zero.
