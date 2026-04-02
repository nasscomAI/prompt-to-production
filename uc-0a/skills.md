# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint record into category, priority, reason, and review flag using the UC-0A schema.
    input: "One complaint row (dict/object) containing complaint description text."
    output: "Object with fields: category (exact allowed value), priority (Urgent|Standard|Low), reason (one sentence with text evidence), flag (NEEDS_REVIEW or blank)."
    error_handling: "If description is missing/empty, return category=Other, priority=Low, reason='Description is missing so classification is uncertain.', flag=NEEDS_REVIEW. If category is ambiguous, choose best fit and set flag=NEEDS_REVIEW."

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint to each row, and writes the output CSV.
    input: "CSV file path (e.g., ../data/city-test-files/test_[your-city].csv) with complaint rows."
    output: "CSV file (e.g., uc-0a/results_[your-city].csv) with added columns: category, priority, reason, flag."
    error_handling: "If file/path is invalid, raise clear file error. If a row is malformed, write row with category=Other, priority=Low, reason explaining malformed input, flag=NEEDS_REVIEW, then continue processing."
