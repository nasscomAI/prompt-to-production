# skills.md — UC-0C Budget Analysis Skills

skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates the structure, and identifies/reports rows where actual_spend is null.
    input: String (path to CSV).
    output: List of dictionaries (cleaned data).
    error_handling: Prints warnings for every null actual_spend row found, including the note.

  - name: compute_growth
    description: Filters data by ward and category, then calculates Month-over-Month (MoM) growth with formula transparency.
    input: Data list, ward name, category name, growth type.
    output: List of dictionaries with period, spend, growth, and formula.
    error_handling: Refuses to aggregate if ward or category are not specific; returns flagged rows for null inputs.
