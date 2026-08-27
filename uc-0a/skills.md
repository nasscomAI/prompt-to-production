# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint into a category and priority, providing justification and ambiguity flag.
    input: A dictionary with keys: 'description' (string).
    output: A dictionary with keys: 'category' (string), 'priority' (string), 'reason' (string), 'flag' (string or blank).
    error_handling: Returns 'category': 'Other' and 'flag': 'NEEDS_REVIEW' if the description is ambiguous or invalid.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying classify_complaint to each row, and writes the results to an output CSV.
    input: Input file path (string) and output file path (string).
    output: Writes a CSV file with columns: 'category', 'priority', 'reason', 'flag'.
    error_handling: Skips rows with invalid data, logs errors, and ensures the output file is complete.
