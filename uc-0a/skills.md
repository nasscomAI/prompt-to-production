# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single civic complaint into a category and priority level based on its description text.
    input: A dictionary representing one CSV row with keys — complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dictionary with keys — complaint_id (passthrough), category (one of 10 allowed values), priority (Urgent/Standard/Low), reason (one sentence citing description words), flag (NEEDS_REVIEW or empty string).
    error_handling: If description is empty or None, return category "Other", priority "Low", reason "No description provided", flag "NEEDS_REVIEW". Never crash on malformed input.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV.
    input: input_path (string — path to test_[city].csv), output_path (string — path to write results CSV).
    output: A CSV file at output_path with columns complaint_id, category, priority, reason, flag. Also prints a summary count of classifications to stdout.
    error_handling: If input file is missing or unreadable, exit with a clear error message. If individual rows fail classification, log the error, write that row with category "Other" and flag "NEEDS_REVIEW", and continue processing remaining rows.
