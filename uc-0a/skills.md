# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint based on its text description into predefined categories and priorities.
    input: A dictionary representing a single complaint row with fields: complaint_id, location, and description.
    output: A dictionary containing complaint_id, category, priority, reason (citing source text), and flag (NEEDS_REVIEW or blank).
    error_handling: If the description is missing, it assigns category 'Other' and sets flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: Absolute or relative path to the input CSV file (e.g., ../data/city-test-files/test_pune.csv).
    output: Writes the classification results to a CSV file at the specified output path (e.g., results_pune.csv).
    error_handling: Validates file existence and CSV structure; logs errors for malformed rows while continuing batch processing where possible.
