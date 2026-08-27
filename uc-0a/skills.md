skills:
  - name: classify_complaint
    description: Classifies one civic complaint into the approved UC-0A category, priority, reason, and review flag.
    input: A dictionary representing one CSV row, expected to include complaint_id and description.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: Return category Other, priority Low, a missing-data reason, and flag NEEDS_REVIEW when required fields are absent or ambiguous.

  - name: batch_classify
    description: Reads a complaint CSV, applies classify_complaint to each row, and writes the standardized result CSV.
    input: Input CSV path and output CSV path.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for every readable input row.
    error_handling: Continue processing after malformed rows, preserve a complaint_id when possible, and emit review-flagged rows instead of crashing.
