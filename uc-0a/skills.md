# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into a category and priority, providing a reason and an optional review flag.
    input: A single row of complaint data (text description).
    output: A structured object containing category, priority, reason, and flag.
    error_handling: If the description is missing or empty, return category 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Path to an input CSV file (e.g., ../data/city-test-files/test_pune.csv).
    output: Path to the generated results CSV file (e.g., results_pune.csv).
    error_handling: Log rows that fail classification and continue processing the remaining rows. Set flag to 'NEEDS_REVIEW' for problematic rows.
