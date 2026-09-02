# skills.md - UC-0C Budget Growth Analyst

skills:
  - name: load_dataset
    purpose: >
      Read the supplied budget CSV, validate its required columns, preserve
      source values, and report every null actual_spend row before any growth
      calculation.
    input:
      type: file path
      format: ".csv budget file path"
      required_columns:
        - period
        - ward
        - category
        - budgeted_amount
        - actual_spend
        - notes
    output:
      type: structured dataset
      contents:
        - "All input rows with exact period, ward, category, budgeted_amount, actual_spend, and notes values preserved."
        - "The dynamically detected total count of blank or null actual_spend values."
        - "A report for every null row containing its period, ward, category, and notes reason."
    expected_behavior:
      - "Read the CSV supplied by the caller rather than relying on a fixed dataset inventory."
      - "Validate that period, ward, category, budgeted_amount, actual_spend, and notes all exist before returning the dataset."
      - "Detect blank or null actual_spend values directly from the loaded rows."
      - "Report the total null count and every detected null row before any growth calculation occurs."
      - "Preserve exact period, ward, and category values, including punctuation, spacing, and en dashes."
      - "Use the corresponding notes value as the null reason."
    constraints:
      - "Never treat a null actual_spend as zero."
      - "Never silently skip a null row or substitute another actual_spend value."
      - "Do not hard-code known null rows, invent null reasons, alter source values, or add business rules."
    error_handling:
      - "Reject a missing or unreadable input file rather than fabricating data."
      - "Reject a CSV missing any required column and identify the missing column names."

  - name: compute_growth
    purpose: >
      Calculate growth for one exact ward and category at the per-period level
      using the explicitly requested growth type.
    input:
      type: structured dataset from load_dataset
      parameters:
        ward: "Exact ward value from the CSV"
        category: "Exact category value from the CSV"
        growth_type: "Explicitly requested supported growth type, including MoM"
    output:
      type: per-period table
      requirements:
        - "Contain rows only for the requested ward and requested category."
        - "Preserve each source period and exact ward/category names."
        - "Include the actual_spend value, calculated growth where valid, formula used, and any null flag/reason."
        - "Show the formula alongside every calculated result."
    expected_behavior:
      - "Require ward, category, and growth_type; never infer a missing growth type."
      - "Reject all-ward, all-category, or cross-group aggregation instead of producing a combined number."
      - "Filter by exact ward and exact category values without guessing or substituting similar names."
      - "For MoM, compare each period with the immediately previous period within the same ward and same category."
      - "Calculate MoM as ((current actual_spend - previous actual_spend) / previous actual_spend) * 100."
      - "If current or previous actual_spend is null, do not calculate growth for that row; flag it and report the applicable notes reason."
      - "Report null rows before calculated growth rows."
      - "Return a deterministic result for identical input rows and parameters."
    constraints:
      - "Never mix wards or categories when selecting the previous period or calculating growth."
      - "Never treat null as zero, silently omit it, or substitute another value."
      - "Do not invent data, formulas, null reasons, growth types, or business rules."
      - "Do not aggregate periods, wards, or categories into a single total."
      - "Every calculated row must include the exact formula used and its result."
    error_handling:
      - "Refuse and ask the caller to specify growth_type when it is missing."
      - "Reject growth types that are not explicitly supported rather than choosing MoM, YoY, or another formula silently."
      - "Reject ward or category values not present in the loaded dataset rather than guessing a match."
      - "Reject a request for all wards or all categories rather than returning an aggregated result."
      - "For a previous or current null actual_spend, emit a flagged non-computed row with the exact notes reason."
