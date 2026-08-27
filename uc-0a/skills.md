skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category, priority, reason, and flag.
    input: complaint row from CSV containing complaint_id and description
    output: dictionary with category, priority, reason, and flag
    error_handling: if category cannot be determined, mark category as Other and flag NEEDS_REVIEW

  - name: batch_classify
    description: Processes the entire complaints dataset and writes classification results to CSV.
    input: input CSV file containing complaint records
    output: results CSV with classification fields added
    error_handling: skips invalid rows and continues processing remaining records