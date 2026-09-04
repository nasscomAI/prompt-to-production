skills:
  - name: load_dataset
    description: Reads budget CSV, validates required columns, reports null counts and affected rows.
    input: File path to ward_budget.csv
    output: List of row dictionaries with parsed numerical types and null flags.
    error_handling: Raises FileNotFoundError if CSV missing; logs null values without skipping rows.

  - name: compute_growth
    description: Filters by ward + category, computes MoM/YoY growth per period, formats formula and flags null spend rows.
    input: dataset rows, ward, category, growth_type ('MoM' or 'YoY')
    output: List of output dictionaries containing computed growth, formula used, and notes.
    error_handling: Refuses calculation if growth_type is missing or if cross-ward aggregation requested.
