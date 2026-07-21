skills:
  - name: classify_complaint
    description: Classifies one complaint row into the exact UC-0A taxonomy with a priority, reason, and review flag.
    input: A dict-like CSV row containing complaint_id, location, description, and any other source columns.
    output: A dict with complaint_id, category, priority, reason, and flag.
    error_handling: Returns category Other and flag NEEDS_REVIEW when the description is blank, malformed, or ambiguous, while still providing a reason.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint row by row, and writes a complete output CSV without aborting on bad rows.
    input: An input CSV path and an output CSV path.
    output: A results CSV with one output row for every readable input row.
    error_handling: Flags rows with missing fields or row-level exceptions as NEEDS_REVIEW, writes a fallback result, and continues processing remaining rows.
