skills:
  - name: classify_complaint
    description: Classifies a single complaint dictionary containing the description and other metadata into the schema format.
    input: dict representing one row from the complaint CSV
    output: dict containing keys: complaint_id, category, priority, reason, flag
    error_handling: If any required fields are missing or if the category is ambiguous, returns category 'Other' and sets the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads the input CSV containing complaints, runs classify_complaint for each row, and writes the output back to a new CSV.
    input: string representing input CSV file path, string representing output CSV file path
    output: None (writes results to output CSV file path)
    error_handling: Handles null/missing fields, doesn't crash on bad rows, and produces output even if some rows fail.
