skills:
  - name: load_dataset
    description: Reads the budget CSV, validates the expected schema, and reports every null actual_spend row with its notes before returning the dataset.
    input: >
      String path to a UTF-8 CSV file (e.g. ../data/budget/ward_budget.csv); optional encoding parameter if needed by the runtime.
    output: >
      Structured tabular data (e.g. rows as records or a dataframe) plus a companion report object listing total null actual_spend count and each affected row’s period, ward, category, and notes text.
    error_handling: >
      On missing or unreadable path, return a clear error and no partial table. On missing or mistyped columns, fail with the list of required columns (period, ward, category, budgeted_amount, actual_spend, notes). Never return data without reporting null actual_spend rows first (no silent null handling). If the caller asks to load or merge data into a single city-wide aggregate, refuse. If the path is ambiguous (e.g. directory instead of file), reject with a specific message.

  - name: compute_growth
    description: Computes growth for exactly one ward and one category using the specified growth type and returns a per-period table with the numeric result and formula on each applicable row.
    input: >
      Filtered budget rows for a single ward string, a single category string, and a required growth_type token (e.g. MoM, YoY); must not be omitted or defaulted.
    output: >
      Per-period table (rows keyed by period) where each row that has a computable growth value includes the growth result and the explicit formula string used; rows with null actual_spend are listed as flagged with the reason taken from notes and no growth value computed for those periods.
    error_handling: >
      If growth_type is missing, empty, or unspecified, refuse execution and ask for a concrete growth_type (never infer MoM vs YoY). If ward or category is missing or matches no rows, report an error or empty scoped result with explanation. For any period with null actual_spend, flag the row and surface notes as the null reason before any growth step (do not silently impute). If input requests aggregation across wards or categories or an all-ward single number, refuse. If growth_type is not supported, fail with allowed values.
