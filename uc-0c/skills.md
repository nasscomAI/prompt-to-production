# skills.md

skills:
  - name: load_dataset
    description: Reads the budget CSV, validates columns (period, ward, category, budgeted_amount, actual_spend, notes), and identifies rows with null actual_spend values.
    input: File path (string) to the CSV file.
    output: A tuple or dictionary containing the validated DataFrame and a summary of null rows with their notes.
    error_handling: Raise an error if the file is missing or if mandatory columns are absent.

  - name: compute_growth
    description: Calculates period-over-period growth (e.g., MoM) for a specific ward and category, incorporating formula transparency and null row flagging.
    input: Ward (string), Category (string), Growth Type (string - MoM/YoY), and Dataset (DataFrame).
    output: A per-period table/CSV structure containing growth results, formula strings, and null flags where applicable.
    error_handling: Refuse computation and request clarification if Growth Type is missing or if an aggregation request violates enforcement rules.
