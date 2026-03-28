skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the UC-0A fixed taxonomy.
    input: "JSON object with required field description:string and optional fields complaint_id:string, ward:string, locality:string, timestamp:string."
    output: "JSON object {category:string, priority:string, reason:string, flag:string} where category and priority are exact allowed labels and reason is one sentence."
    error_handling: "If description is missing or empty, return category: Other, priority: Standard, reason explaining missing input, and flag: NEEDS_REVIEW. If category is ambiguous, return category: Other and flag: NEEDS_REVIEW."

  - name: batch_classify
    description: Reads the city test CSV, applies classify_complaint row-by-row, and writes results CSV in the required schema.
    input: "Input CSV path and output CSV path. Input rows must include a description column for each complaint."
    output: "Output CSV with all original rows plus classification columns: category, priority, reason, flag; returns summary metadata {rows_processed:int, rows_flagged:int, output_path:string}."
    error_handling: "If file path is invalid or CSV is malformed, stop with a clear error message and do not emit partial silent outputs. Rows with missing description are written with category: Other and flag: NEEDS_REVIEW so processing can continue."
