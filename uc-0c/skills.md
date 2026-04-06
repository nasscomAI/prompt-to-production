# skills.md — UC-0C: Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns
      (period, ward, category, budgeted_amount, actual_spend, notes) are
      present, and reports the null count and which rows have null
      actual_spend before returning the DataFrame.
    input: >
      file_path (str): Absolute or relative path to the CSV file.
      ward (str): The ward to filter on (e.g., "Ward 1 – Kasba").
      category (str): The budget category to filter on (e.g., "Roads & Pothole Repair").
    output: >
      filtered_df (DataFrame): Filtered DataFrame for the requested ward +
      category, sorted by period ascending.
      null_report (list[dict]): List of dicts for each null actual_spend row,
      each containing {period, ward, category, reason} extracted from notes.
    error_handling: >
      If the CSV is missing any required column, raise ValueError with the
      list of missing columns.
      If --ward or --category does not match any value in the dataset, raise
      ValueError listing all valid wards or categories.
      If file_path does not exist or is unreadable, raise FileNotFoundError.

  - name: compute_growth
    description: >
      Takes a filtered per-ward per-category DataFrame and a growth type
      (MoM, QoQ, or YoY), computes the period-over-period growth rate for
      actual_spend, and returns a table with the formula shown for every row.
    input: >
      filtered_df (DataFrame): Output of load_dataset — single ward, single
      category, sorted by period.
      growth_type (str): One of "MoM", "QoQ", or "YoY".
    output: >
      result_df (DataFrame): One row per period with columns:
      period, ward, category, actual_spend, growth_rate, formula, null_flag.
      - growth_rate: percentage string (e.g., "+33.1%") or "NULL — not computed".
      - formula: arithmetic string (e.g., "MoM: (19.7 - 14.8) / 14.8 * 100 = 33.1%").
      - null_flag: "NULL" with reason if actual_spend is missing, empty otherwise.
      The first period has growth_rate = "N/A — no prior period".
      If current or prior period actual_spend is null, growth_rate = "NULL — not computed".
    error_handling: >
      If growth_type is not one of MoM, QoQ, or YoY, raise ValueError
      listing the valid options.
      If the filtered DataFrame is empty (no matching data), raise
      ValueError with a message indicating no data found for the given
      ward + category combination.
