skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a valid category, assigns a priority, provides a reason, and flags ambiguous complaints for manual review.
    input: A dictionary representing one complaint record from the input CSV, including complaint_id and description.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the complaint description is missing, empty, or cannot be confidently classified, return category as Other, set flag to NEEDS_REVIEW, provide an appropriate reason, and continue processing.

  - name: batch_classify
    description: Reads all complaint records from an input CSV, classifies each complaint using classify_complaint, and writes the results to an output CSV
    input: Input CSV file path and output CSV file path.
    output: A CSV file containing complaint_id, category, priority, reason, and flag for every processed complaint.
    error_handling: Skip malformed rows safely, continue processing the remaining records, and ensure the output CSV is generated even if some rows contain errors.
