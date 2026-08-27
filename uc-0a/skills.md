skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a predefined category, assigns priority, extracts a reason, and flags ambiguity.
    input: A single citizen complaint record (e.g., dictionary or string) containing the complaint description.
    output: A structured object containing 'category' (from exact allowed list), 'priority' (Urgent, Standard, Low), 'reason' (one sentence citing specific words), and 'flag' (NEEDS_REVIEW or blank).
    error_handling: Sets 'flag' to 'NEEDS_REVIEW' if the complaint is genuinely ambiguous or if the category is unclear.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the classifications to an output CSV.
    input: File path to an input CSV file (e.g., '../data/city-test-files/test_[your-city].csv').
    output: Writes processed rows with their classifications to an output CSV file (e.g., 'results_[your-city].csv').
    error_handling: Handles missing data gracefully and proceeds with processing remaining rows; logs errors if input file is not found.