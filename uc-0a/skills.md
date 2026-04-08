# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a predefined taxonomy of categories and priorities based on its description.
    input: A dictionary representing a complaint row, containing at least a 'description' field.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is missing or the category cannot be determined with high confidence, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification of a batch of complaints from an input CSV file and writes the results to an output CSV file.
    input: Paths to the input CSV file and the desired output CSV file.
    output: None (results are written directly to the output file).
    error_handling: Must flag nulls in required fields, not crash on malformed or bad rows, and ensure the output CSV is produced even if individual row classifications fail.
