# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies one citizen complaint into an allowed category and priority, provides an evidence-based reason, and flags ambiguous or invalid complaints for review.
    input: A single complaint row as a dict containing complaint_id and complaint description, with optional date, city, ward, location, reported_by, and days_open fields.
    output: A dict containing complaint_id, category, priority, reason, and flag.
    error_handling: Missing or invalid complaint data must not crash classification; return category Other, priority Standard, an explanatory reason, and flag NEEDS_REVIEW. Genuinely ambiguous categories are also flagged for review.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to every complaint row, and writes the classification results to an output CSV.
    input: Input CSV file path containing citizen complaint rows and output CSV file path for the classification results.
    output: CSV containing complaint_id, category, priority, reason, and flag for every input row.
    error_handling: Invalid rows must not stop processing of the remaining rows; each failed row receives a safe Other/Standard classification with NEEDS_REVIEW, and the output CSV is still written.