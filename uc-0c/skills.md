# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates columns, and reports null count and which rows have null actual_spend before returning data.
    input: file_path (str, path to ward_budget.csv).
    output: Parsed data as a list of dicts, plus a report of null rows (count, which ward/category/period, and the reason from notes).
    error_handling: If required columns are missing, prints an error and exits. If file not found, prints an error and exits.

  - name: compute_growth
    description: Takes a ward + category + growth_type (MoM or YoY), filters the dataset, and returns a per-period growth table with formula shown.
    input: ward (str), category (str), growth_type (str, "MoM" or "YoY"), and the loaded dataset.
    output: A list of dicts with keys period, ward, category, actual_spend, previous_spend, growth_rate, formula, notes_flag. Written to output CSV.
    error_handling: If ward or category not found in data, prints available values and exits. If growth_type is not MoM or YoY, refuses and asks user to specify. Null actual_spend rows get growth_rate="N/A — null data" with reason.
