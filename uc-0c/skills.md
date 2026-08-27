# skills.md
# Budget Growth Calculation Skills

skills:
  - name: load_dataset
    description: Reads budget CSV, validates columns exist, counts and flags all null actual_spend rows before returning data.
    input: CSV file path (string); returns full DataFrame including null rows with notes column.
    output: Pandas DataFrame with all rows; list of null row indices with (period, ward, category, notes); null count.
    error_handling: Raises ValueError if columns missing; stops execution if file not found; reports all null rows and their reasons before continuing.

  - name: validate_request
    description: Validates that growth-type is specified (MoM or YoY), refuses ambiguous requests, and ensures only single ward + single category requested.
    input: ward (string), category (string), growth_type (string or None).
    output: Boolean (valid=True/False); refusal message if invalid.
    error_handling: Refuses if growth_type is None/empty and prompts user. Refuses if multiple wards/categories detected. Returns clear error message.

  - name: compute_growth
    description: Calculates MoM or YoY growth for a single ward + category, showing formula in each output row.
    input: DataFrame with (period, ward, category, actual_spend); ward (string), category (string), growth_type ('MoM' or 'YoY').
    output: DataFrame with columns [period, actual_spend, previous_period, formula, growth_percent]; flags any nulls encountered.
    error_handling: Preserves nulls in output (shows NULL in formula column); does not impute or skip null rows silently — always flags them explicitly.
