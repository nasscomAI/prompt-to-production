skills:
  - name: classify_complaint
    description: Analyzes one citizen complaint row and classifies it into a category, assigns priority, provides a reason citing specific words, and flags if ambiguous.
    input: String - Plain text description of one civic complaint.
    output: JSON object containing 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: If input format is invalid, returns all fields as empty.

  - name: batch_classify
    description: Reads an input CSV of multipe complaint rows, applies the classify_complaint skill to each row, and writes the results to an output CSV.
    input: String - Path to the input CSV file. String - Path to the output CSV file.
    output: Boolean - True if batch processing completes successfully and writes file.
    error_handling: Halts processing and logs an error if the input CSV file is missing or invalid.
