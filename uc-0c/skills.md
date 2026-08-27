# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV budget file, validates columns, and explicitly reports the total null count and specific rows containing nulls before returning the data.
    input: file_path (string) - The path to the CSV dataset (e.g., `../data/budget/ward_budget.csv`).
    output: A tuple containing `dataset` (list of records) and `null_report` (metadata specifying which rows have null `actual_spend` and their associated `notes`).
    error_handling: If the file is unreadable or missing required columns, immediately raise an error. Deliberately stops to flag any null values found rather than silently coercing them to zero or ignoring them.

  - name: compute_growth
    description: Calculates budget growth metrics strictly for a specified ward and category, returning a per-period table that includes the explicit formula used for each row.
    input: `dataset` (list of records), `ward` (string), `category` (string), `growth_type` (string, e.g., "MoM" or "YoY").
    output: `growth_table` (list/CSV) containing the period, actual spend, computed growth, and the formula used to calculate it.
    error_handling: Strictly refuses to guess if `growth_type` is not specified. Refuses to execute if asked to aggregate across all wards or categories without explicit instruction. If a period involves a null `actual_spend`, it flags the row as "NULL" and refuses to compute a misleading growth figure.
