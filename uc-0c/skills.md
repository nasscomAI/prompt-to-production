skills:
  - name: load_dataset
    description: Reads the ward budget CSV file, parses data types, and generates an audit report of null or missing actual_spend rows.
    input: File path string pointing to ward_budget.csv dataset.
    output: Parsed list of row dictionaries and a list of identified null/missing data records.
    error_handling: Raises file error if path invalid, or reports missing columns if required CSV headers are missing.

  - name: compute_growth
    description: Filters data by specific ward and category, calculates Month-over-Month (MoM) growth rates, and flags null spend rows without aggregation.
    input: Parsed dataset from load_dataset, target ward string, target category string, and growth type string ('MoM').
    output: List of dictionaries containing period, ward, category, budgeted_amount, actual_spend, mom_growth, and notes.
    error_handling: If ward is set to 'ALL' or empty, refuses execution with an unaggregated scope error; if actual_spend is null, sets mom_growth to 'NULL (Flagged)'.
