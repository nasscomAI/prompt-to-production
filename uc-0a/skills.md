skills:
  - name: classify_complaint
    description: Analyzes a dictionary row to determine category, priority, and reason based on strict urban triage rules.
    input: Dictionary row containing 'description' and 'location'.
    output: Dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: Flags ‘NEEDS_REVIEW’ if the description is missing or ambiguous.

  - name: batch_classify
    description: Reads a city CSV, applies classification per row, and writes results to a local CSV.
    input: Input CSV path and output CSV path.
    output: Success status and generated result file.
    error_handling: Ensures the script completes even if specific rows are malformed.
