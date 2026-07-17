skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns
      (period, ward, category, budgeted_amount, actual_spend, notes)
      are present, and reports null count and which rows have missing
      actual_spend before returning the parsed dataset.
    input: file_path (string) — absolute or relative path to ward_budget.csv.
    output: >
      dataset (list of dicts) — every row from the CSV, plus a printed
      summary listing total row count, null actual_spend count, and per-null
      row detail (period, ward, category, notes reason).
    error_handling: >
      Exits with error if the file does not exist or if any required column
      is missing from the CSV header.

  - name: compute_growth
    description: >
      Filters the dataset to a single ward + category pair, sorts by period,
      and computes month-over-month growth. Returns a per-period table with
      the formula shown alongside each result.
    input: >
      dataset (list of dicts) — the parsed budget data.
      ward (string) — exact ward name to filter on.
      category (string) — exact category name to filter on.
      growth_type (string) — must be 'MoM'; any other value is refused.
    output: >
      growth_table (list of dicts) — one row per period with keys: Ward,
      Category, Period, Actual Spend (₹ lakh), MoM Growth, Formula.
    error_handling: >
      Refuses if growth_type is missing or unsupported. Refuses if ward or
      category is omitted, empty, or set to an aggregation keyword (all, any,
      *, combined, total, aggregate). Flags null actual_spend rows with the
      reason from notes; flags the following month as uncomputable when the
      previous month's actual_spend is null.
