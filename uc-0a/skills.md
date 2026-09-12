skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a category, priority, and reason based on its description.
    input: A dict representing one complaint row, containing complaint_id, date_raised, city, ward, location, and description fields
    output: A dict with keys complaint_id, category, priority, and reason
    error_handling: If the description field is missing or empty, flag the row rather than confidently guessing a category

  - name: batch_classify
    description: Reads the full input CSV, classifies every row using classify_complaint, and writes all results to an output CSV.
    input: File path (string) to the input CSV and file path (string) for the output CSV
    output: A CSV file with columns complaint_id, category, priority, and reason for every input row
    error_handling: Must not crash on a malformed or bad row — flag that row's reason field with an error note and continue processing the remaining rows