# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag fields.
    input: Dictionary with keys 'complaint_id', 'description', 'date_raised', 'city', 'ward', 'location' (CSV row as dict).
    output: Dictionary with keys 'complaint_id', 'category', 'priority', 'reason', 'flag'. Category must be from allowed list. Priority is Urgent/Standard/Low. Reason is one sentence citing description words. Flag is NEEDS_REVIEW or blank.
    error_handling: If description is null/empty, set category=Other, priority=Standard, reason='No description provided', flag=NEEDS_REVIEW. If description is ambiguous across multiple categories, set flag=NEEDS_REVIEW and choose best-fit category.

  - name: batch_classify
    description: Read input CSV, classify each row via classify_complaint, write results CSV with all columns plus classifications.
    input: File path to test_[city].csv (CSV with columns from input file).
    output: File path to write results_[city].csv (all input columns plus category, priority, reason, flag columns).
    error_handling: Continue on malformed rows — log them with category=Other, flag=NEEDS_REVIEW. Never crash the batch process. Output file always produced even if some rows fail to classify.
