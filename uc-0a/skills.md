skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag.
    input: A dictionary containing complaint_id and description (string).
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing or unclear, assigns category as "Other", sets flag to "NEEDS_REVIEW", and provides a fallback reason.

  - name: batch_classify
    description: Processes a CSV file of complaints and applies classify_complaint to each row.
    input: Input CSV file path containing complaint rows with description field.
    output: Output CSV file with columns complaint_id, category, priority, reason, and flag.
    error_handling: Skips or safely handles malformed rows, ensures output file is still generated, and flags problematic entries.