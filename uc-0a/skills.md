skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and flag using strict schema rules.
    input: dict containing complaint row fields (complaint_id, description, etc.)
    output: dict with keys complaint_id, category, priority, reason, flag
    error_handling: Fallback to category 'Other' and set flag 'NEEDS_REVIEW' if category is ambiguous or fields are missing.

  - name: batch_classify
    description: Reads complaints from an input CSV file, applies classification to each row, and writes results to an output CSV.
    input: str (input_path), str (output_path)
    output: None (writes file to output_path)
    error_handling: Flags empty/null descriptions, logs and skips malformed rows, and ensures processing continues despite single-row failures.
