skills:
  - name: load_dataset
    description: Reads budget CSV data, validates schema, and reports null count and flagged rows before downstream processing.
    input: File path (str) to ward_budget.csv.
    output: Tuple or dict containing parsed records and a detailed inventory of all flagged null rows with notes.
    error_handling: Raises FileNotFoundError if missing; flags and isolates corrupted rows without silent dropping.

  - name: compute_growth
    description: Computes period-over-period budget expenditure growth for a specified ward and category with transparent formula reporting.
    input: Filter parameters (ward, category, growth_type) and dataset records.
    output: List of dictionaries representing per-period table with actual_spend, growth percentage, calculation status, and explicit formula string.
    error_handling: Refuses calculation if ward or category is omitted (refuses all-ward aggregation), refuses if growth_type is unspecified, and explicitly marks null/uncomputable periods with the reason from notes.
