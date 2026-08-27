# skills.md — UC-0C Infrastructure Growth Computator

skills:
  - name: load_dataset
    description: Safely reads the CSV budget dataset, checks for data completeness, and profiles missing information.
    input: File path (string) pointing to the dataset (e.g., `ward_budget.csv`).
    output: A DataFrame or list of dictionary records containing the active subset of data requested.
    error_handling: Systematically validates columns, explicitly reports the null count, and surfaces which rows are missing `actual_spend` before proceeding.

  - name: compute_growth
    description: Calculates the period-over-period growth per the specified growth type for the filtered subset, safely skipping or tagging null rows.
    input: The filtered dataset, the designated `ward` string, the `category` string, and the `growth_type` string.
    output: A per-period table (e.g., list of dicts) with output rows encompassing period, ward, category, base value, growth result, and the explicit mathematical formula used.
    error_handling: Raises an explicit exception if asked to aggregate broadly, or if `growth_type` is undefined/unrecognized. Safely cascades null flags into the output alongside the notes.
