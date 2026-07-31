skills:
  - name: load_dataset
    description: Reads the budget CSV dataset, validates required columns, identifies null actual_spend rows, and returns filtered record sets.
    input: CSV file path (str), ward name (str), category name (str)
    output: List of row dictionaries and list of identified null record warnings
    error_handling: Refuses processing if file is missing, invalid, or requires unapproved cross-ward rollups.

  - name: compute_growth
    description: Computes period-over-period growth rates (MoM or YoY) for filtered records, attaching formulas and null flags.
    input: Filtered row records (list of dicts), growth_type (str)
    output: List of dictionaries with computed growth percentages, formula strings, and notes
    error_handling: Flags missing prior-period data or null spend as uncomputed NULL with notes retained.
