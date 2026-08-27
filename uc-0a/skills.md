skills:
  - name: classify_complaint
    description: Classify a single sentence complaint into a row with fields category, priority, reason, and flag by applying keyword-based rules from README.md
    input: A dictionary representing one complaint row with fields: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: A dictionary with fields complaint_id, category, priority, reason, flag
    error_handling: If required complaint fields are missing or empty then return category as Other, priority as Low, reason explaining the missing input, and flag as NEEDS_REVIEW. If the complaint is ambiguous return category as Other and flag as NEEDS_REVIEW.

  - name: batch_classify
    description: Process a CSV file containing rows of complaints, apply classify_complaint to each row, and produce output rows as in UC-0A results
    input: Use the file ../data/city-test-files/test_pune.csv
    output: Create a CSV file to contain the fields: complaint_id, category, priority, reason, flag. Save the file as results_pune.csv
    error_handling: Skip rows that cannot be parsed and include a diagnostics entry if applicable. For ambiguous rows, rely on classify_complaint to return category as Other and flag as NEEDS_REVIEW