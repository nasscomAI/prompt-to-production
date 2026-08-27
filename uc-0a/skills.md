# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category and priority with a cited reason.
    input: A JSON object or dictionary containing 'description' and optional metadata from the complaint row.
    output: A dictionary with 'category' (allowed strings only), 'priority' (Urgent/Standard/Low), 'reason' (single sentence citation), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: If the description is empty, set category to 'Other' and flag to 'NEEDS_REVIEW'. If ambiguous, assign best guess and flag for review.

  - name: batch_classify
    description: Reads a CSV file of complaints, classifies each row using classify_complaint, and writes the results to a new CSV.
    input: Path to an input CSV file (e.g., ../data/city-test-files/test_[city].csv).
    output: Path to an output CSV file (e.g., uc-0a/results_[city].csv) containing the original columns plus category, priority, reason, and flag.
    error_handling: Handles file not found errors and ensures all rows are processed even if individual classifications encounter ambiguity.
