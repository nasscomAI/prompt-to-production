# skills.md

skills:
  - name: load_dataset
    description: Reads the CSV dataset, validates necessary columns, and reports on the completeness of the data before downstream processing.
    input: Filepath string pointing to the dataset (e.g., `../data/budget/ward_budget.csv`).
    output: Parsed structured dataset and a validation report containing the total null count and stating exactly which rows have null `actual_spend` values.
    error_handling: If the file is missing or required columns (period, ward, category, budgeted_amount, actual_spend, notes) are absent or misformatted, throw a fatal error. Do not proceed with processing on corrupted data.

  - name: compute_growth
    description: Calculates growth metrics for a strictly specified ward and category based on an explicitly provided calculation type.
    input: The parsed dataset from `load_dataset`, the target `ward`, the target `category`, and the `growth_type`.
    output: A per-period output table detailing the raw figures, computed growth, and explicitly showing the mathematical formula used for every row.
    error_handling: If `growth_type` is not specified, refuse to calculate, do not guess a default (like MoM/YoY), and prompt the user. If an `actual_spend` value is null for a computed period, explicitly flag the row with the reason from the `notes` column rather than silently skipping it or assigning it zero.
