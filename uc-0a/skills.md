# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category, priority, reason, and optional review flag using only the description text.
    input: A dictionary with keys: complaint_id, date_raised, city, ward, location, description, reported_by.
    output: A dictionary with keys: category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing specific words from description), flag (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or missing, set category to Other and flag to NEEDS_REVIEW. If the description contains no recognizable complaint signals, set priority to Low and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies classify_complaint to each row, and writes the classified results to an output CSV.
    input: File path to an input CSV containing columns: complaint_id, date_raised, city, ward, location, description, reported_by.
    output: A new CSV file at the specified output path containing all input columns plus: category, priority, reason, flag.
    error_handling: If the input file is missing or unreadable, raise a clear error with the file path. If any row fails classification, log the complaint_id and continue processing remaining rows — do not abort the batch on a single row failure.
