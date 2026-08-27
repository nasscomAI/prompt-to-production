skills:
  - name: classify_complaint
    description: Classifies one complaint row into constrained taxonomy with urgency and review flag.
    input: One CSV row as a dictionary with complaint_id and description.
    output: Dictionary with complaint_id, category, priority, reason, flag.
    error_handling: Returns category Other and flag NEEDS_REVIEW when ambiguous or malformed.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, and writes output CSV.
    input: input_path and output_path strings.
    output: Output CSV with one result row per input row.
    error_handling: Catches per-row exceptions and writes fallback row instead of crashing.
