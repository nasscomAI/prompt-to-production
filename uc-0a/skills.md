# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into category, priority, reason, and optional flag.
    input: A plain-text string containing the citizen complaint description.
    output: A dict/row with keys category (one of 10 allowed strings), priority (Urgent/Standard/Low), reason (one sentence citing specific words from input), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or unparseable, return category: Other and flag: NEEDS_REVIEW. If description does not clearly map to a supported category, return category: Other and flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV with complaint descriptions, applies classify_complaint per row, and writes the output CSV with classified columns added.
    input: A CSV file path. The CSV must contain a column with complaint descriptions (column name configurable).
    output: A CSV file written to the specified output path, containing all original columns plus category, priority, reason, and flag.
    error_handling: Skips malformed rows with a warning, includes them in output with category: Other, priority: Low, flag: NEEDS_REVIEW. Reports total processed and failed counts at completion.
