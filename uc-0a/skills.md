# UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into a valid category, priority, reason, and review flag.
    input: A complaint row as a dictionary containing the complaint description and related fields.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the complaint is invalid or the category is genuinely ambiguous, classify it as Other and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file, classifies every complaint row, and writes the results to an output CSV file.
    input: Input CSV file path and output CSV file path.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for every processed row.
    error_handling: Handles missing or bad rows without crashing and continues processing the remaining rows.