# skills.md - UC-0C Ward Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and reports null actual_spend rows before returning data.
    input: Path to a CSV file with period, ward, category, budgeted_amount, actual_spend, and notes columns.
    output: A tuple containing all data rows and the subset of rows where actual_spend is null.
    error_handling: Raises a validation error if required columns are missing; blank actual_spend values are reported with their period, ward, category, and notes reason.

  - name: compute_growth
    description: Computes period-over-period growth for one explicit ward and category using the requested growth type.
    input: Dataset rows, exact ward string, exact category string, and explicit growth_type string.
    output: A per-period table with actual spend, previous period spend, formula, growth percent, flag, and null reason.
    error_handling: Refuses all-ward or all-category aggregation, refuses missing or unsupported growth types, and flags rows with current null, previous null, or previous zero actual_spend instead of computing.
