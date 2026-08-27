# skills.md

skills:
  - name: classify_complaint
    description: Categorizes and prioritizes a single city service complaint based on its description.
    input: A dictionary representing a CSV row, including at least a 'description' field.
    output: A dictionary with 'category', 'priority', 'reason', and 'flag' keys.
    error_handling: Sets category to 'Other' and flag to 'NEEDS_REVIEW' if description is missing or genuinely ambiguous.

  - name: batch_classify
    description: Processes a CSV file of complaints and writes the classified results to a new CSV file.
    input: String path to the input CSV and string path for the output CSV.
    output: None (writes to file).
    error_handling: Handles missing files and ensures the output file is generated even if individual rows have errors.
