# skills.md — UC-0C Ward Budget Growth Calculator Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required columns, inspects null `actual_spend` values, and reports null count and affected rows before returning.
    input: `file_path` (str, path to CSV file, e.g., `ward_budget.csv`).
    output: Tuple containing parsed row dictionaries and a null report list specifying affected periods, wards, categories, and notes explanations.
    error_handling: If the input file is missing, unreadable, or missing required headers (`period`, `ward`, `category`, `budgeted_amount`, `actual_spend`), raises a ValueError or FileNotFoundError.

  - name: compute_growth
    description: Calculates per-period budget spend growth for a specific ward and category based on the specified growth type (MoM or YoY), including explicit formulas and null flags.
    input: `data` (list of row dicts), `ward` (str), `category` (str), and `growth_type` (str, e.g., `MoM` or `YoY`).
    output: List of formatted row dictionaries containing `ward`, `category`, `period`, `actual_spend`, `growth_pct`, `formula_used`, and `flag_notes`.
    error_handling: Refuses execution if cross-ward/cross-category aggregation is requested, or if `growth_type` is omitted/unspecified. Flags null spend rows as `NULL` without computing growth and includes the reason from the `notes` column.
