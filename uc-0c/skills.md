# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Reads budget CSV, validates columns, and reports null count and location before processing.
    input: File path to ward_budget.csv.
    output: Clean list of row dictionaries with parsed float/null actual_spend values.
    error_handling: Identifies and tags blank actual_spend values with notes column reasons.

  - name: compute_growth
    description: Calculates per-period growth rates for a filtered ward and category using specified growth-type.
    input: Filtered budget rows, target ward, target category, and growth_type (MoM or YoY).
    output: Table/CSV containing period, ward, category, actual_spend, growth_pct, formula, and flags.
    error_handling: Refuses unguided requests without growth_type or requests attempting cross-ward aggregation.

