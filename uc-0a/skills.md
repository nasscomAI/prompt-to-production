skills:
  - name: classify_complaint
    description: Classifies a single complaint description into category and priority.
    input: A dictionary representing one CSV row containing complaint_id and description.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the description is empty or ambiguous, classify as Other and set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a CSV file of complaints, classifies each row, and writes the results to a new CSV file.
    input: Input CSV path containing complaint rows.
    output: Output CSV containing classification results for each complaint.
    error_handling: If a row cannot be processed, the classifier still writes the row with category Other and flag NEEDS_REVIEW.