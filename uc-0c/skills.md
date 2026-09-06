skills:
  - name: load_dataset
    description: Reads the municipal budget CSV file, validates required schema headers, and audits all null actual_spend rows citing explanations from the notes column.
    input: File path string pointing to ward_budget.csv.
    output: Tuple containing the complete list of parsed row dictionaries and a list of audited null records.
    error_handling: Handles text encoding variations (UTF-8, Latin-1) without corruption; raises descriptive errors if required columns (period, ward, category, actual_spend) are missing.

  - name: compute_growth
    description: Computes period-over-period expenditure growth for a specified ward and category using an explicit growth formula.
    input: List of row dictionaries, target ward string, target category string, and growth_type string (e.g. 'MoM').
    output: List of structured result dictionaries containing period, ward, category, budgeted_amount, actual_spend, growth_rate, and calculation_formula.
    error_handling: Refuses immediately if ward or category are omitted or set to aggregate 'All'; refuses if growth_type is missing; safely flags periods with null current or prior values without throwing unhandled exceptions.
