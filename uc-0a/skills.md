# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint description into the required structural fields.
    input: One complaint description/row (string or structured row).
    output: The row appended with category, priority, reason, and flag fields based on the exact classification schema.
    error_handling: If the text is genuinely ambiguous, assign an appropriate or 'Other' category and append NEEDS_REVIEW in the flag field.

  - name: batch_classify
    description: Iterates through the input CSV file, applies the classify_complaint skill per row, and reliably writes the results to the output CSV file.
    input: The input CSV file path (e.g., ../data/city-test-files/test_[your-city].csv).
    output: Generates a CSV file at the output path (e.g., uc-0a/results_[your-city].csv) containing all classified rows.
    error_handling: Handle file not found errors when reading the CSV and halt if writing permissions are denied for the output CSV.
