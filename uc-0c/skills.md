# skills.md
skills:
  - name: load_dataset
    description: Safely reads the budget CSV, validates column structures, and immediately intercepts and reports all null data points.
    input: An absolute or relative path to a CSV dataset.
    output: A validated, loaded dataset array with a pre-calculation summary of missing actual_spend rows including their specific notes.
    error_handling: Halts the pipeline completely if the CSV scheme is unrecognized or missing mandatory columns.

  - name: compute_growth
    description: Executes scoped temporal growth calculations (MoM or YoY) strictly partitioned by user-provided Ward and Category parameters.
    input: The validated dataset array, target ward string, target category string, and an explicit growth_type.
    output: A restricted per-period table indicating the formula applied, prior period values, current values, and calculated growth or explicit null flags.
    error_handling: Immediately raises a refusal alert if asked to aggregate multiple wards or categories, or if growth_type is blank/invalid.
