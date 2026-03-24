# skills.md

skills:
  - name: load_dataset
    description: Opens and ingests the CSV dataset exactly, validates columns, and explicitly audits the total count and contextual mappings of deliberate null values before computation.
    input: Absolute or relative filepath pointing to the budget source CSV data.
    output: Returns a structured row matrix of dict representations, printing a specific logging audit trace of every detected null actual_spend row.
    error_handling: Immediately halts execution and dumps an error boundary string if the file is poorly formatted or schema elements are completely missing.

  - name: compute_growth
    description: Enforces constrained MoM / YoY computation mappings exclusively isolating calculation onto identical `ward` and `category` boundaries, printing formulas explicitely per row.
    input: Pre-filtered exact-matching rows, paired with an explicitly supplied growth_type argument.
    output: A newly formulated per-period dataset row table holding specific `growth` and explicit `formula` outputs based on calculation states.
    error_handling: Systematically blocks execution if boundaries are "ANY" or missing. Bypasses calculations sequentially upon detecting a null `actual_spend` metric, routing notes directly into formula markers.
