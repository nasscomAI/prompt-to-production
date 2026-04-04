skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint based on its description into predefined categories and priorities.
    input: A single description string from a CSV row.
    output: A JSON object containing category, priority, reason, and flag.
    error_handling: Returns category: Other and flag: NEEDS_REVIEW if ambiguous or description is insufficient.

  - name: batch_classify
    description: Automates the classification of multiple complaints by reading an input CSV and writing the results to an output CSV.
    input: Path to a source CSV file and a destination CSV path.
    output: Generates a CSV file following the project's classification schema.
    error_handling: Logs failures and ensures every output row contains all fields: category, priority, reason, and flag.
