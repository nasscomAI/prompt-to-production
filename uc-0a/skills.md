skills:
  - name: classify_complaint
    description: Classifies one complaint description into UC-0A schema fields with evidence-based reasoning.
    input: "One complaint row (dict/object) containing free-text description; optional row_id accepted."
    output: "Object with category, priority, reason, and flag using only allowed schema values."
    error_handling: "If description is missing/empty, return category=Other, priority=Low, reason='Description is missing or empty.', flag=NEEDS_REVIEW. If category evidence is ambiguous, set category=Other and flag=NEEDS_REVIEW."

  - name: batch_classify
    description: Reads the UC-0A input CSV, applies classify_complaint per row, and writes a results CSV.
    input: "Input CSV path with complaint descriptions; expected 15 rows per city test file."
    output: "Output CSV path with one result row per input row including category, priority, reason, and flag."
    error_handling: "If input file cannot be read or required description column is absent, raise a clear validation error and do not write partial output. For malformed rows, continue processing with row-level fallback from classify_complaint and mark NEEDS_REVIEW."