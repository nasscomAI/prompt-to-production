# UC-0C Budget Analysis Skills

skills:
  - name: load_dataset
    description: Reads the municipal budget CSV, validates essential columns, and identifies all rows with missing actual spend data to ensure transparency.
    input: Absolute path to the budget CSV file.
    output: A structured collection of budget rows along with a report of null counts and specific null-row identifiers.Must be a per-ward per-category table — not a single aggregated number.
    error_handling: Raises an error if mandatory columns are missing or if the file is unreadable.

  - name: compute_growth
    description: Calculates financial growth (MoM or YoY) for a specific ward and category, explicitly displaying the formula used and flagging null-row interruptions.
    input: Ward name, category name, growth type (MoM/YoY), and the structured dataset.
    output: A period-by-period table showing actual spend, the growth percentage, and the explicit formula used.
    error_handling: Refuses calculation for periods involving null values (reporting the reason from notes) or if the growth type is unspecified.

