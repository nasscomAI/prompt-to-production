skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason, and flag using the fixed UC-0A schema.
    input: "object with complaint text fields (minimum: description string; optional metadata allowed)."
    output: "object with fields: category (allowed taxonomy only), priority (Urgent|Standard|Low), reason (one sentence citing complaint words), flag (NEEDS_REVIEW or blank)."
    error_handling: "If description is empty, non-text, or too ambiguous to map confidently, return category=Other, priority=Standard unless severity keywords force Urgent, reason explaining uncertainty from available text, and flag=NEEDS_REVIEW."

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a result CSV.
    input: "CSV file path containing complaint rows (for UC-0A: test_[city].csv with category and priority_flag removed)."
    output: "CSV file path written with one output row per input row and required fields category, priority, reason, flag."
    error_handling: "For malformed rows, continue processing remaining rows, write row-level fallback output with flag=NEEDS_REVIEW, and avoid introducing out-of-schema category or priority values."
