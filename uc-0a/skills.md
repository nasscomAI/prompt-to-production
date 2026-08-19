skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason justification, and review flag based on RICE enforcement rules.
    input: A dictionary representing a complaint row with fields such as complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dictionary containing original complaint fields plus category (exact allowed string), priority (Urgent/Standard/Low), reason (one sentence citing description words), and flag (NEEDS_REVIEW or blank).
    error_handling: If description is missing, empty, or genuinely ambiguous, category defaults to 'Other', flag is set to 'NEEDS_REVIEW', and reason states missing or ambiguous context.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, processes each row via classify_complaint, and writes the structured classification results to an output CSV.
    input: Absolute or relative file paths for input CSV (e.g., test_[city].csv) and output CSV (e.g., results_[city].csv).
    output: Creates/overwrites output CSV containing classified complaints with all original columns plus category, priority, reason, and flag.
    error_handling: Handles missing input files, empty rows, or row processing errors gracefully without crashing the overall batch run, flagging problematic rows with NEEDS_REVIEW.
