skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason and flag.
    input: One complaint row from the CSV file as a dictionary.
    output: complaint_id, category, priority, reason, flag.
    error_handling: If category is unclear, return category as Other and flag as NEEDS_REVIEW.

  - name: batch_classify
    description: Processes all complaint rows and generates a classified output CSV.
    input: Input CSV containing complaint records.
    output: CSV containing complaint_id, category, priority, reason and flag.
    error_handling: Invalid rows are flagged as NEEDS_REVIEW and processing continues without crashing.