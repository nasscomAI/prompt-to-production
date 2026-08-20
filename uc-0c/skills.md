skills:
  - name: load_dataset
    description: Reads the municipal ward budget CSV dataset, validates schema and column types, and reports all null/missing actual_spend rows along with reasons from notes.
    input: File path to ward_budget.csv (str).
    output: Parsed list of row dictionaries and a list of identified null records with explanations (dict).
    error_handling: Raises FileNotFoundError if the file is missing, and flags invalid numeric formats without crashing.

  - name: compute_growth
    description: Computes period-over-period spend growth strictly for a specified ward and category using an explicitly requested formula (e.g. MoM), displaying the formula and flagging null periods.
    input: Dataset rows (list), target ward (str), target category (str), growth_type (str).
    output: List of processed rows containing period, ward, category, budgeted_amount, actual_spend, growth_pct, formula, notes, and status (list).
    error_handling: Refuses all-ward aggregation requests and halts if growth_type is omitted or invalid.
