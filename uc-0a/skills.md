# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dictionary with keys from input CSV (complaint_id, description, city,ward,location,reported_by,days_open, etc.).
    output: A dictionary with keys category, priority, reason, flag, and complaint_id.
    error_handling: If description is missing or empty, category=Other, priority=Low, reason="Insufficient description", flag=NEEDS_REVIEW. If multiple categories match, set flag=NEEDS_REVIEW and choose the most likely category.

  - name: batch_classify
    description: Reads input CSV rows, applies classify_complaint, and writes the results CSV.
    input: input CSV file path and output CSV file path.
    output: A CSV at output path with columns complaint_id, category, priority, reason, flag.
    error_handling: Skips invalid rows with warning, continues processing, and includes placeholder row with flag=NEEDS_REVIEW on parse error.

