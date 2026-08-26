# skills.md

skills:
  - name: classify_complaint
    description: Classify one citizen complaint into an allowed category and priority with an evidence-based reason and review flag.
    input: One complaint row as a dictionary containing complaint_id and complaint description fields.
    output: Dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the row is missing or the description is invalid, return a safe Other classification with NEEDS_REVIEW rather than crashing.

  - name: batch_classify
    description: Read complaint records from a CSV file, classify each row, and write the classification results to a CSV file.
    input: Input CSV path containing complaint rows and output CSV path for the classification results.
    output: CSV containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Handle missing or malformed rows without crashing the entire batch, mark uncertain rows for review, and still produce the output CSV.
