# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into a category and priority level with justification.
    input: Dictionary with keys (complaint_id, description) and optional fields (date_raised, city, ward, location, reported_by, days_open).
    output: Dictionary with keys (complaint_id, category, priority, reason, flag) where category is one of the 10 allowed values, priority is Urgent/Standard/Low, reason cites specific description words, and flag is empty string or 'NEEDS_REVIEW'.
    error_handling: If description is missing or empty, returns category='Other', priority='Low', reason='No description provided', flag='NEEDS_REVIEW'. If description is ambiguous, returns best guess category with flag='NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads complaint CSV file, classifies all rows using classify_complaint, and writes results to output CSV.
    input: Two strings - input_path (path to CSV with complaint data) and output_path (path for results CSV).
    output: Writes CSV file with columns (complaint_id, category, priority, reason, flag) and prints confirmation message.
    error_handling: Skips rows with missing complaint_id but logs warning to stderr. Continues processing remaining rows even if individual classifications fail. Always produces output file even if some rows fail.
