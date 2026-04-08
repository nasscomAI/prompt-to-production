skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, priority, reason, and flag.
    input: A single complaint row containing a textual description. Type: Dictionary/JSON or Text Row.
    output: Returns a structured record containing 'category', 'priority', 'reason', and 'flag'. Type: Dictionary/JSON.
    error_handling: If the text is missing or completely unreadable, default category to 'Other', set priority to 'Standard', reason to 'Invalid or missing input', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV, applies classify_complaint to each row, and writes the output to a CSV.
    input: File path to an input CSV containing citizen complaints. Type: String (File Path).
    output: Writes a CSV file containing the classifications and returns the output file path. Type: String (File Path).
    error_handling: If the input file is not found or unreadable, halt the process and raise an error. For individual row errors, handle via the classify_complaint error rules.
