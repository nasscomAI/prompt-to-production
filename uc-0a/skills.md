# skills.md

skills:
  - name: classify_complaint
    description: Parses a citizen complaint accurately to assign taxonomy category, priority urgency, exact reasoning, and review flags.
    input: Dictionary row from the CSV representing one complaint, including a text description.
    output: Dictionary with the standardized 'category', 'priority', 'reason', and 'flag' assignments.
    error_handling: Assigns 'Other' category and 'NEEDS_REVIEW' flag for ambiguous classifications or no matching keywords.

  - name: batch_classify
    description: Opens a CSV file of complaints, iterates over it applying classification_complaint per row, and exports the resultant dataset.
    input: Two strings representing the file paths for the input CSV and output CSV.
    output: None (writes to the specified output CSV on disk).
    error_handling: Handles malformed rows by capturing errors gracefully, assigning an ERROR flag if a specific row crashes, and proceeding with the batch.
