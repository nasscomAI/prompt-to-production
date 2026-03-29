# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, and returns filtered rows with null handling metadata.
    input: file_path (string)
    output: list of dictionaries with keys [period, ward, category, budgeted_amount, actual_spend, notes, missing_flag, missing_reason]
    error_handling: raise FileNotFoundError if file missing; raise ValueError if required column missing; mark rows with null actual_spend and include notes in missing_reason while continuing processing.

  - name: compute_growth
    description: Computes growth for a specified ward/category and growth_type (MoM, YTD, or YoY) up to a specified end period and returns a per-period table with formula and null flags. Note: YoY requires previous year data (not available in current dataset).
    input: dataset (list of dicts), ward (string), category (string), growth_type (string: MoM/YTD/YoY), end_period (string: YYYY-MM, optional, defaults to latest)
    output: list of dictionaries with keys [period, actual_spend, budgeted_amount, growth_value, growth_formula, status, notes]
    error_handling: raise ValueError if growth_type missing or unsupported; refuse (raise ValueError) if ward/category not provided; skip but flag null actual_spend rows using status 'NULL' and include notes; if end_period is invalid, raise ValueError; for YoY, raise ValueError if previous year data not available.

  - name: validate_no_aggregate
    description: Verifies that the request is not attempting all-ward/category aggregation unless explicitly allowed.
    input: ward (string), category (string), allow_aggregate (bool)
    output: bool (True if valid), message (string)
    error_handling: if allow_aggregate is False and ward/category are missing, return False with refusal message; otherwise return True.

