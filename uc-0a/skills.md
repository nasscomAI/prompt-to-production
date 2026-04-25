# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single urban complaint into a category and priority level while providing a cited reason.
    input: A dictionary representing a single complaint row (e.g., {'description': '...'}).
    output: A dictionary containing category, priority, reason, and flag (e.g., {'category': 'Pothole', 'priority': 'Standard', 'reason': '...', 'flag': ''}).
    error_handling: If the description is empty, missing, or genuinely ambiguous, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a city's complaint CSV file.
    input: Path to the input CSV file (e.g., '../data/city-test-files/test_pune.csv').
    output: Path to the generated results CSV file (e.g., 'results_pune.csv').
    error_handling: Validates file existence before processing; catches and logs row-level classification errors without stopping the batch.
