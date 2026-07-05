# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into standard category, priority, and reason fields, with ambiguity flagging.
    input: A dictionary representing a single complaint row (keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open).
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If required fields are missing or the description is blank/null/ambiguous, sets category to 'Other', priority to 'Standard', reason to a descriptive message, and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file containing citizen complaints, processes each row using classify_complaint, and writes the output to a results CSV file.
    input: Path to the input CSV file (string) and path to the output CSV file (string).
    output: None (writes results directly to output CSV).
    error_handling: Flags null input rows, does not crash on malformed lines, and logs/continues execution ensuring output is generated even if specific rows fail.
