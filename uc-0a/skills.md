# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row based on a predefined taxonomy and priority rules.
    input: dictionary representing a single complaint row (e.g. from a CSV read)
    output: dictionary with keys: complaint_id, category, priority, reason, flag
    error_handling: set category to 'Other' and flag to 'NEEDS_REVIEW' if the category is ambiguous or cannot be determined.

  - name: batch_classify
    description: Read an input CSV, classify each row using classify_complaint, and write the results to an output CSV.
    input: input_path (str), output_path (str)
    output: none (side effect: writes results_Pune.csv or similar)
    error_handling: flag nulls, do not crash on invalid rows, ensure output is written even if some rows fail.
