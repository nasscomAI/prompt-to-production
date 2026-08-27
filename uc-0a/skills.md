# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one complaint description into category, priority, reason, and flag using the fixed UC-0A schema.
    input: "One complaint row containing free-text description (string)."
    output: "Object with fields: category (approved label), priority (Urgent|Standard|Low), reason (one sentence citing source words), flag (NEEDS_REVIEW or blank)."
    error_handling: "If description is empty or not parseable, return category=Other, priority=Standard, reason='Insufficient complaint detail to classify reliably.', flag=NEEDS_REVIEW. If category is ambiguous, use Other + NEEDS_REVIEW."

  - name: batch_classify
    description: Read the city test CSV, apply classify_complaint to each row, and write a results CSV.
    input: "Input CSV path like ../data/city-test-files/test_[city].csv with complaint rows to classify."
    output: "Output CSV at uc-0a/results_[city].csv with one output row per input row including category, priority, reason, and flag."
    error_handling: "Fail fast with a clear error when input file is missing or unreadable. For per-row ambiguity, do not drop the row; emit Other + NEEDS_REVIEW and continue processing remaining rows."
