skills:
  - name: load_dataset
    description: Ingests ward_budget.csv, validates the required schema columns, identifies any null actual_spend values, and logs their occurrences alongside their notes.
    input: File path to ward_budget.csv.
    output: Clean list of row dictionaries with parsed numeric fields, identified null records, and validation metadata.
    error_handling: Raises FileNotFoundError if missing; raises ValueError if required columns are missing.

  - name: compute_growth
    description: Filters data for a specific ward and category, sorts by period chronologically, and computes growth rate using the specified growth type (MoM) while flagging null periods.
    input: Filtered rows, selected ward, selected category, and growth_type ('MoM' or 'YoY').
    output: List of enriched rows containing period, actual spend, computed growth percentage, exact formula string, and null status flags.
    error_handling: Refuses calculation and outputs clear error if growth_type is missing or if requested to aggregate across multiple wards.