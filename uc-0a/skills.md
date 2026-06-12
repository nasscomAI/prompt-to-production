skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row based on rules for category, priority, and ambiguity.
    input: dict representing a single CSV row with keys like complaint_id, description, days_open, etc.
    output: dict containing keys complaint_id, category, priority, reason, flag.
    error_handling: If input fields are missing or invalid (e.g. empty description), default to category: Other, priority: Standard, flag: NEEDS_REVIEW, and reason: "Missing or invalid description".

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint for each row, and writes the results to an output CSV.
    input: string paths for input CSV and output CSV.
    output: Writes output CSV containing complaint_id, category, priority, reason, flag.
    error_handling: Catches reading/writing errors and ensures bad rows do not crash the application, continuing to process subsequent rows.
