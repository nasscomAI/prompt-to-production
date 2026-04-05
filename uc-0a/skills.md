skills:
  - name: classify_complaint
    description: Analyzes a single municipal complaint description to determine category, priority, and justification.
    input: String containing the raw complaint description.
    output: JSON object with keys: category, priority, reason, and flag.
    error_handling: Assigns 'Other' category and 'NEEDS_REVIEW' flag if the description is ambiguous.

  - name: batch_classify
    description: Processes an entire CSV file of city complaints and writes the results to a new output CSV.
    input: Path to the input test CSV file (e.g., test_pune.csv).
    output: A generated results CSV file (e.g., results_pune.csv).
    error_handling: Skips rows with fatal data errors and logs them to ensure processing completes.
