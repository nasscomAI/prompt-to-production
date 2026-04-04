# skills.md — UC-0C Financial Math Agent

skills:
  - name: load_dataset
    description: Reads the budget CSV, safely filters it by explicit parameters, and performs pre-computation null validation.
    input: 
      - filepath (str): Path to CSV data.
      - ward (str): The requested ward name (e.g. "Ward 1 – Kasba").
      - category (str): The requested category (e.g. "Roads & Pothole Repair").
    output: 
      - list of dict: A filtered subset of rows matching the requested parameters exactly.
    error_handling: 
      If ward or category are not specific valid strings (e.g., 'Any'), or are omitted, raises an explicit refusal to aggregate. Traces total data matched vs totally null values present in the slice.

  - name: compute_growth
    description: Strictly computes parametric growth (MoM/YoY), appending formula logic and handling NULL notes directly into the tabular output without omitting bad data.
    input: 
      - rows (list of dict): Cleaned / validated output of load_dataset.
      - growth_type (str): Usually "MoM". Cannot be empty or inferred.
    output: 
      - list of dict: The final tabular output with fields [ward, category, period, actual_spend, growth_value, formula_trace, flags].
    error_handling: 
      If growth_type is unknown or missing, throws a refusal error. If actual_spend is null for a row, sets growth_value to NULL and maps the formula_trace to the CSV notes reason.
