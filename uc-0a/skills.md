# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category and priority, with a reason and ambiguity flag.
    input: A dictionary representing a single row of complaint data, including the 'description' field.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the input is missing a description or is completely unintelligible, set category to 'Other', priority to 'Low', reason to 'Invalid input', and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: File paths for the input CSV and output CSV as strings.
    output: Writes a CSV file with the classification results and returns nothing.
    error_handling: Flags nulls, catches exceptions to avoid crashing on malformed rows, and ensures output is produced for all successfully processed rows even if some fail.
