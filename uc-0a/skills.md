skills:
  - name: classify_complaint
    description: Classify a single complaint text by assigning a category, priority level, justification reason, and manual review flag.
    input: Dictionary representing a single CSV row with keys like complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Return Other category, default Standard/Low priority, and flag as NEEDS_REVIEW if input is missing or cannot be categorized.

  - name: batch_classify
    description: Read all citizen complaints from an input CSV file, classify each complaint, and write the consolidated results to an output CSV file.
    input: File paths for the input CSV and output CSV.
    output: Generates a CSV file containing columns complaint_id, category, priority, reason, flag.
    error_handling: Handles empty files and individual row parsing failures without crashing, logging warnings for skipped/failed rows.
