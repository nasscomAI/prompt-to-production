# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify one citizen complaint into an approved category and priority, provide an evidence-based reason, and flag genuinely ambiguous cases.
    input: One complaint row as a dictionary containing complaint_id and complaint description, with other provided row fields allowed as context.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If the input is missing required complaint information or the category cannot be determined confidently, return a safe result using category Other and flag NEEDS_REVIEW rather than crashing.

  - name: batch_classify
    description: Classify all complaint rows from an input CSV and write one structured result row for each complaint to an output CSV.
    input: Input CSV file containing citizen complaint rows.
    output: CSV containing complaint_id, category, priority, reason, and flag for every input complaint.
    error_handling: Handle missing or malformed rows without crashing the batch; flag affected rows for review and continue processing the remaining complaints.