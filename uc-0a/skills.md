skills:
  - name: classify_complaint
    description: Maps a single municipal complaint to a specific category, priority level, and single-sentence justification citing the source.
    input: Row object containing the citizen complaint description and stripped classification fields.
    output: Object populated with category, priority, one-sentence reason, and an ambiguity flag.
    error_handling: Escalates priority to Urgent if severity keywords are present and sets NEEDS_REVIEW if the category is genuinely ambiguous to prevent false confidence.

  - name: batch_classify
    description: Iteratively processes a CSV file of complaints, applying classification logic to each row and writing the final structured results.
    input: File path to a CSV containing complaint descriptions with 15 rows per city.
    output: File path to the results_city.csv file containing the full structured taxonomy.
    error_handling: Enforces strict adherence to the exact category strings to prevent taxonomy drift and validates the presence of justification metadata for every row.
