# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: One complaint row in -> category + priority + reason + flag out.
    input: A dictionary representing a single complaint row with a 'description' field.
    output: A dictionary containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: Handles empty descriptions by setting category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: A file path string pointing to the input CSV.
    output: Writes results to a new CSV file and prints completion message.
    error_handling: Notifies if input file is missing and handles exceptions during CSV processing.
