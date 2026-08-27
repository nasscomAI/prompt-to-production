# skills.md — UC-0C Ward Budget Growth Analyzer

skills:
  - name: load_dataset
    description: Reads an input CSV containing municipal ward budget and spend records, verifies required columns and types, and scans for null/missing `actual_spend` values, logging the total null count and specific row details with explanations from the `notes` column prior to downstream processing.
    input: `input_path` (str, path to the input CSV file containing columns `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`).
    output: tuple of (`df` (list of dicts or DataFrame containing parsed records with standardized types), `null_records` (list of dicts capturing each null row's `period`, `ward`, `category`, and `notes` reason)).
    error_handling: Raises `FileNotFoundError` if the CSV file does not exist; raises `ValueError` if required columns are missing, if the dataset is empty, or if file formatting is corrupted.

  - name: compute_growth
    description: Calculates granular period-over-period financial growth rates (e.g., MoM or YoY) for a designated ward and expenditure category, producing a per-period output table where each row displays the actual figures, percentage growth rate, substituted formula, and null flag details.
    input: `dataset` (list of dicts or DataFrame), `ward` (str, specific ward name), `category` (str, specific category name), `growth_type` (str, 'MoM' or 'YoY'), `null_records` (list of dicts from `load_dataset`).
    output: list of dicts (or DataFrame / CSV output table) containing columns `period`, `ward`, `category`, `budgeted_amount`, `actual_spend`, `growth_type`, `growth_rate_pct`, `formula_used`, `flag`, and `notes`.
    error_handling: Refuses computation and raises `ValueError` if `growth_type` is not specified or unrecognized (never guesses); refuses and raises `ValueError` if `ward` or `category` is missing or requests an all-ward/cross-category aggregation; flags rows with missing current or prior spend as `NULL_SPEND_NOT_COMPUTED`, sets `growth_rate_pct: NULL`, and populates `notes` with the recorded justification instead of silent zero-filling or omitting rows.
