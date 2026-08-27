skills:
  - name: classify_complaint
    description: Classifies a single raw complaint description into a structured output (category, priority, reason, flag) following the official schema.
    input: Dictionary representing a single CSV row with at least a 'description' field.
    output: Dictionary containing 'category', 'priority', 'reason', and 'flag' based on the enforcement rules in agents.md.
    error_handling: Returns 'Unknown' for category and priority if input is empty or ambiguous; returns 'Out of Scope' if the complaint is unrelated to city services.

  - name: batch_classify
    description: Automatically processes an entire CSV file of citizen complaints by applying the single-row classifier to each entry and saving the aggregated results to a new file.
    input: String representing the absolute path to the input CSV file.
    output: String representing the absolute path to the generated output CSV file containing the classifications.
    error_handling: Validates file existence and schema compatibility; handles missing data by assigning error-state classifications (e.g., Unknown) to ensure full file processing.
