skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a category and priority level, providing a reason and flag if ambiguous.
    input: A dictionary representing a single complaint row (e.g., {'complaint_id': '...', 'description': '...'}).
    output: A dictionary containing the keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is ambiguous and cannot be mapped to a known category, output category 'Other' and set flag to 'NEEDS_REVIEW'. Do not guess or hallucinate categories.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies the classify_complaint skill to each row, and writes the results to a new CSV file.
    input: Two strings representing the file paths: 'input_path' (path to the input CSV) and 'output_path' (path to write the results CSV).
    output: None (writes to a file).
    error_handling: Must flag null rows. Must not crash on bad or malformed rows; it should handle exceptions gracefully, perhaps logging them, and ensure the process continues so that valid rows are still outputted.