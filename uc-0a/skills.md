# skills.md

skills:
  - name: classify_complaint
    description: Transforms a single raw CSV row into a structured classification object.
    input: row (Dict) - containing at least 'complaint_id' and 'description'.
    output: result (Dict) - keys: complaint_id, category, priority, reason, flag.
    error_handling: |
      If 'description' is missing, empty, or genuinely ambiguous, set category: 'Other' 
      and flag: 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates reading the input CSV, applying classify_complaint per row, and writing the final CSV.
    input: input_path (String), output_path (String).
    output: None (Writes to filesystem).
    error_handling: |
      Must flag nulls, not crash on bad rows, and ensure the process completes 
      even if individual rows fail.
