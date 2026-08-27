# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: Complaint description string and metadata (row data).
    output: category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence), flag (NEEDS_REVIEW or blank).
    error_handling: If category cannot be determined from description, output category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: CSV file path with complaint descriptions.
    output: CSV file with classified rows (category, priority, reason, flag columns).
    error_handling: For any row that fails classification, apply fallback (Other + NEEDS_REVIEW) and continue processing remaining rows.