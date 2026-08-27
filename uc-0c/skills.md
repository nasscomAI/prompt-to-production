skills:
  - name: load_dataset
    description: Read the budget CSV, validate required schema, and report null actual_spend rows before any computation.
    input: "CSV file path string (expects columns: period, ward, category, budgeted_amount, actual_spend, notes)."
    output: "Validated dataset object plus summary: total rows, distinct wards/categories, null count, and list of null rows with period, ward, category, and notes."
    error_handling: "Fail fast with a structured error if file is missing, unreadable, or required columns are absent; do not continue to growth computation on schema failure."

  - name: compute_growth
    description: Compute growth by period for one ward and one category using an explicit growth type and formula display per row.
    input: "Validated dataset object plus ward string, category string, and required growth_type string (for example, MoM or YoY)."
    output: "Per-period table for the selected ward/category with period, actual_spend, growth_result, and formula_used; null rows are flagged and not computed."
    error_handling: "Refuse when growth_type is missing/ambiguous, ward/category is missing, or a request implies all-ward/all-category aggregation without explicit override; return actionable clarification prompts."
