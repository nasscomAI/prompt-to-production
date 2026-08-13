skills:
  - name: classify_complaint
    description: Analyzes a single civic complaint's description to determine its category, priority, reason, and review flag.
    input: dict containing complaint row (with at least 'description' and 'complaint_id' keys)
    output: dict containing keys: complaint_id, category, priority, reason, flag
    error_handling: Falls back to category 'Other' and sets flag 'NEEDS_REVIEW' if the input description is missing, empty, or ambiguous.

  - name: batch_classify
    description: Reads complaints from an input CSV, processes each row using classify_complaint, and writes the results to an output CSV.
    input: input_path (str) to source CSV, output_path (str) to destination CSV
    output: None (writes results file)
    error_handling: Handles empty or invalid rows gracefully without crashing, logging errors and continuing batch processing.
