# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description and returns structured classification data including category, priority, reason, and status flags.
    input: A dictionary containing at least a 'description' field.
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If the description is empty or nonsense, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an input CSV file of complaints, applies classification to each row, and writes the results to an output CSV file.
    input: Path to the input CSV file and path to the output CSV file.
    output: Writes a CSV file with classified results and prints a completion message.
    error_handling: Skips invalid rows and continues processing; handles file not found errors gracefully.
