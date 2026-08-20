skills:
  - name: load_dataset
    description: Reads and parses municipal budget CSV data, validates required schema columns, counts total rows, and identifies all NULL actual_spend rows with notes.
    input: String file path 'input_path' pointing to source CSV file.
    output: List of row dictionaries with parsed numerical floats for budgeted_amount and actual_spend (or None for NULL values).
    error_handling: Raises FileNotFoundError if CSV missing; flags corrupt or unparseable numeric values with error notes.

  - name: compute_growth
    description: Computes per-period MoM or YoY growth rates for a specific ward and category, generating a transparent analytical output table.
    input:
      dataset: List of parsed row dictionaries from load_dataset.
      ward: Target ward string (e.g. 'Ward 1 – Kasba').
      category: Target category string (e.g. 'Roads & Pothole Repair').
      growth_type: Calculation type string ('MoM' or 'YoY').
    output: List of output dictionaries containing period, ward, category, budgeted_amount, actual_spend, growth_type, growth_percentage, formula, and flag_notes.
    rule_enforcement:
      aggregation_prevention: Refuses if ward or category is 'ALL' or empty.
      null_handling: Sets growth_percentage to 'N/A (Data Missing)' for NULL actual_spend rows and includes notes.
      formula_disclosure: Includes exact mathematical formula string on every output row.
    error_handling: Refuses execution if growth_type is not explicitly set to 'MoM' or 'YoY'.
