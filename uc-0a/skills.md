skills:
  - name: classify_complaint
    description: Classifies an individual municipal complaint row into an approved category, priority, justification reason, and review flag.
    input: Dictionary containing complaint fields (complaint_id, description, etc.).
    output: Dictionary with keys (complaint_id, category, priority, reason, flag).
    error_handling: Falls back to category 'Other' and sets flag to 'NEEDS_REVIEW' if the input description is missing, empty, or ambiguous.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint per record, handles missing/corrupt rows, and writes the structured results CSV.
    input: File paths for input CSV (string) and destination output CSV (string).
    output: Writes compliant output CSV file containing all classified records.
    error_handling: Handles missing fields and null rows safely without crashing, logging errors and assigning default fallback classifications.