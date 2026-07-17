# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Maps one complaint description to the required category, priority, reason, and review flag.
    input: A dictionary row from the complaint CSV containing at least the description field.
    output: A dictionary with complaint_id, category, priority, reason, and flag.
    error_handling: If the description is empty or does not fit a known category, assign Other and set NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes a results CSV.
    input: Path to the input CSV and path to the output CSV.
    output: A CSV file containing one classified row per input complaint.
    error_handling: If a row cannot be classified, preserve the row and mark it for review rather than crashing the batch.
