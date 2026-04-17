skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint description into the city's infrastructure taxonomy and determines priority level.
    input: Dictionary representing a single complaint row (must include a 'description' field).
    output: Dictionary containing 'category' (allowed string), 'priority' (Urgent/Standard/Low), 'reason' (single sentence with citation), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the description is empty or genuinely ambiguous, categorize as 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the classification of an entire CSV file containing citizen complaints.
    input: String path to the input CSV file (e.g., '../data/city-test-files/test_pune.csv').
    output: String path to the generated results CSV file (e.g., 'results_pune.csv').
    error_handling: Handles file access errors, malformed CSV rows, and halts with descriptive errors if the input format does not match the expected schema.
