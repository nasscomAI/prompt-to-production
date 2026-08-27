skills:
  - name: classify_complaint
    description: Classifies a single complaint description into a specific category, priority, and reasons, flagging ambiguity if found.
    input:
      type: dict
      format: CSV row containing 'complaint_id' and 'description'
    output:
      type: dict
      format: keys 'complaint_id', 'category', 'priority', 'reason', 'flag'
    error_handling:
      invalid_input: If description is missing, set category to Other, priority to Low, reason to 'Missing description', and flag to NEEDS_REVIEW.
      ambiguous: If the complaint matches multiple categories, set flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads the input complaints CSV, classifies each row using classify_complaint, and writes the output CSV.
    input:
      type: str
      format: path to the input CSV file
    output:
      type: str
      format: path to the output CSV file
    error_handling:
      missing_file: Raise FileNotFoundError if input path doesn't exist.
      empty_rows: Log and skip empty rows, ensuring process doesn't crash on invalid data.
