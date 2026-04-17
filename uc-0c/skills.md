# skills.md

skills:
  - name: load_dataset
    description: Safely reads the `ward_budget.csv`, rigidly validating schema and logging exact locations of missing values.
    input: File path to the dataset.
    output: Returns a structured dataset strictly maintaining its raw form while logging the total count of null values, their row indices, and reporting the provided `notes` column for each.
    error_handling: Halts processing entirely and throws an error if raw schema is corrupted or missing.

  - name: compute_growth
    description: Executes isolated financial growth calculations for specific configurations without dropping silently or assuming mathematical formulas.
    input: Requires exactly `ward`, `category`, and explicitly defined `growth_type` parameters.
    output: A per-period table outputting calculation results combined identically with the mathematical formula generated per row logic.
    error_handling: Systematically blocks computations by returning flat refusals if a parameter (like growth_type) is ambiguous/null, or if an aggregation across isolated wards or categories is attempted.
