# skills.md

skills:
  qa  - name: classify_complaint
    description: Processes a single complaint description to determine its category, priority, and justification, strictly adhering to the UC-0A taxonomy.
    input: A dictionary containing at least the 'description' field (string).
    output: >
      A dictionary containing:
      - 'category': Exact string from the allowed list (e.g., 'Pothole', 'Flooding').
      - 'priority': Exact string ('Urgent', 'Standard', 'Low').
      - 'reason': A single sentence citing specific words from the description.
      - 'flag': 'NEEDS_REVIEW' if ambiguous, otherwise an empty string.
    error_handling: >
      If description is empty, missing, or genuinely ambiguous, return category: 'Other' and flag: 'NEEDS_REVIEW'.
      If any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) is present, the priority must be 'Urgent'.
      If the description is too vague to classify, refuse to guess and use 'Other'/'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes a CSV of complaints, applying 'classify_complaint' to each row and generating a standardized results file.
    input: Path to a CSV file (e.g., '../data/city-test-files/test_pune.csv').
    output: Path to the generated results CSV file (e.g., 'results_pune.csv').
    error_handling: >
      Validates that the input CSV contains a 'description' column.
      Ensures the output CSV contains all required columns: description, category, priority, reason, flag.
      Logs any rows that failed processing for manual audit.
