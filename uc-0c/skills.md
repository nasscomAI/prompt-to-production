skills:
  - name: load_dataset
    description: "Read the ward budget CSV, validate its columns, and report null actual_spend values before calculation."
    input: "Path to ward_budget.csv."
    output: "Validated dataset plus null count, affected rows, and each row's notes reason."
    error_handling: "Reject missing columns, unreadable files, invalid numbers, or an empty dataset with a specific diagnostic; never coerce null actual_spend to zero."

  - name: compute_growth
    description: "Compute the requested growth type for one ward and category at the per-period level."
    input: "Validated dataset, one ward, one category, and an explicit supported growth_type such as MoM."
    output: "Per-period table containing values, formula text, computed growth where valid, and null or insufficient-history flags."
    error_handling: "Refuse broad aggregation, missing growth type, unknown ward or category, and null calculations; explain the exact reason in the result."
