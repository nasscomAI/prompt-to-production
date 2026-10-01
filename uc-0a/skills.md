skills:
  - name: classify_complaint
    description: Classifies a single complaint record into category, priority, reason, and status flag based on its description and metadata.
    input: A dictionary containing the keys complaint_id, date_raised, city, ward, location, description, reported_by, and days_open.
    output: A dictionary containing the keys complaint_id, category, priority, reason, and flag.
    error_handling: Fallback category to Other and flag to NEEDS_REVIEW if description is missing or category is ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of complaints, classifies each row, and writes the classified records to an output CSV file.
    input: Paths to input CSV file and output CSV file.
    output: Writes the results to the output CSV file.
    error_handling: Logs rows that fail to process and continues execution without crashing.
