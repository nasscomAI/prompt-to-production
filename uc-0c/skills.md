skills:
  - name: load_dataset
    description: Reads the ward_budget.csv, validates required columns are present, filters to the requested ward+category pair, reports total null count and which specific rows have null actual_spend (with their period and notes reason) before returning the filtered data.
    input: |
      - file_path: str — absolute or relative path to ward_budget.csv
      - ward: str — exact ward name to filter on
      - category: str — exact category name to filter on
    output: |
      - filtered_df: DataFrame — rows matching ward+category only, sorted by period
      - null_rows: list[dict] — list of {period, notes} for every row with null actual_spend
      - null_count: int — total number of null actual_spend rows in the filtered set
    error_handling: |
      - Raises ValueError if required columns (period, ward, category, actual_spend, notes) are missing.
      - Raises ValueError if no rows match the given ward+category combination.
      - Prints a pre-computation null report listing every null row before returning data.

  - name: compute_growth
    description: Takes the filtered DataFrame from load_dataset plus an explicit growth_type and returns a per-period table with actual_spend, growth_rate (%), and the full formula string used for each row.
    input: |
      - filtered_df: DataFrame — output from load_dataset (single ward + category)
      - growth_type: str — must be exactly "MoM" or "YoY"; no default, no inference
      - ward: str — ward name (for output labelling)
      - category: str — category name (for output labelling)
    output: |
      - result_df: DataFrame with columns:
          period, ward, category, actual_spend, growth_rate, formula
      - Null rows: growth_rate = "NULL", formula = "N/A (null — <reason from notes>)"
      - First valid period: growth_rate = "N/A (first period)", formula = "N/A (first period)"
      - All other rows: growth_rate = e.g. "+33.1%", formula = e.g. "(19.7 - 14.8) / 14.8 * 100 = +33.1%"
    error_handling: |
      - Raises ValueError if growth_type is not "MoM" or "YoY" — never guesses or defaults.
      - If previous period is also null, uses that period's null flag in the formula column
        and sets growth_rate = "NULL (prev period also null)".
      - Never uses budgeted_amount in any calculation.
