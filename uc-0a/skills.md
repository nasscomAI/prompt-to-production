# UC-0A Complaint Classifier — skill definitions

skills:
  - name: classify_complaint
    description: Classify one complaint row into the UC-0A schema with category, priority, reason, and flag.
    input: A dictionary representing a complaint row with fields such as complaint_id, description, city, ward, location, reported_by, and days_open.
    output: A dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: If the description is missing or the category cannot be determined confidently, return category "Other" with flag "NEEDS_REVIEW" and a reason explaining the issue.

  - name: batch_classify
    description: Read the input CSV of complaints, classify every row using classify_complaint, and write the output CSV.
    input: input_path (path to the source CSV) and output_path (path to the target results CSV).
    output: A CSV file containing complaint_id, category, priority, reason, and flag.
    error_handling: Continue processing after any malformed rows, mark failures as NEEDS_REVIEW, and preserve valid output for remaining rows.
