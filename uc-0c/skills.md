skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates that all required columns are present, and reports the total null count and the exact list of null rows (period · ward · category · null reason from notes) before returning the dataset.
    input: File path string pointing to ward_budget.csv; expected columns — period (YYYY-MM), ward, category, budgeted_amount, actual_spend, notes.
    output: Validated dataset object plus a null-manifest listing each null actual_spend row with its period, ward, category, and notes reason; raises an error if any expected column is missing.
    error_handling: If the file path is invalid or any required column is absent, halt and report the specific issue — do not proceed with partial data. If actual_spend is blank for any row, include that row in the null-manifest; never zero-fill or impute.

  - name: compute_growth
    description: Takes a ward, a category, and an explicit growth_type (MoM or YoY), then returns a per-period growth table with the actual_spend value, the computed growth rate, and the exact formula used for every row.
    input: ward (string, must exactly match a ward in the dataset), category (string, must exactly match a category in the dataset), growth_type (enum — "MoM" or "YoY"; required, never defaulted).
    output: Per-period table with columns — period, actual_spend (value or NULL flag), growth_rate (percentage or NULL flag), formula (e.g., "MoM = (current − previous) / previous × 100"), null_reason (from notes column, populated only when actual_spend is null).
    error_handling: If growth_type is not provided, refuse to proceed and ask the user to specify MoM or YoY explicitly. If the requested ward or category does not exist in the dataset, return a clear error identifying the unmatched value. If a null row is encountered during computation, emit a flagged row with the null_reason and skip the rate calculation for that row only — do not skip adjacent rows or halt the entire computation.
