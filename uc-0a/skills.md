# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single municipal complaint row into a category and priority level with a citation-based justification.
    input: A dictionary representing a single row from the input CSV, containing at least 'complaint_id' and 'description'.
    output: A dictionary containing 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the category is ambiguous or cannot be determined from the description, set 'category' to 'Other' and 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of complaints, applying classification to each row and saving the results to a new CSV.
    input: Path to the input CSV file (string) and path to the desired output CSV file (string).
    output: A CSV file containing classified complaints with columns 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Must handle null values, avoid crashing on malformed rows, and ensure the output file is generated even if individual row classifications fail.

