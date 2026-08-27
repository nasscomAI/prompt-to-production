skills:
  - name: load_dataset
    description: "reads CSV, validates columns, reports null count and which rows before returning"
    input:
      type: string
      format: "file path (e.g., ../data/budget/ward_budget.csv)"
    output:
      type: dictionary
      format: "table data object and validation report with null flags"
    error_handling:
      missing_values: "Flag every null row and report null reason from the notes column."
      zero_division: "Not applicable during load stage."
      incomplete_rows: "Report rows with missing required identifiers."

  - name: compute_growth
    description: "takes ward + category + growth_type, returns per-period table with formula shown"
    input:
      type: dictionary
      format: "{ ward: string, category: string, growth_type: string }"
    output:
      type: list
      format: "per-period table including results and formula trace"
    error_handling:
      missing_values: "Do not compute missing actual_spend. Output NULL and flag appropriately."
      zero_division: "Return 'N/A' or appropriate flag if previous period value is 0 to avoid crashing."
      incomplete_rows: "Refuse aggregation across wards or categories if row details are incorrectly scoped."
