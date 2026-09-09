skills:
  - name: "load_dataset"
    description: "Reads the budget CSV file, validates required schema columns, and scans for null actual_spend rows while extracting explanation notes."
    input:
      file_path: "string (path to CSV dataset)"
    output:
      records: "list of dictionaries containing dataset rows"
      null_flags: "list of dictionaries detailing period, ward, category, and null reason notes"
    error_handling: "If the input file is missing or schema columns are invalid, raise FileNotFoundError or ValueError with explicit error details."

  - name: "compute_growth"
    description: "Calculates per-period budget growth (MoM or YoY) for a target ward and category, displaying formulas and preserving null flags."
    input:
      records: "list of dictionaries (parsed CSV data)"
      ward: "string (target ward name)"
      category: "string (target category name)"
      growth_type: "string (MoM or YoY)"
    output:
      growth_table: "list of dictionaries containing period, ward, category, actual_spend, growth_rate, status, and formula_used"
    error_handling: "Refuse execution and raise ValueError if growth_type is omitted, or if requested parameters imply multi-ward aggregation."