# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint based on its description, determining is category, priority, reason, and any needed flags.
    input: String containing the complaint description.
    output: A dictionary object with keys: category, priority, reason, and flag.
    error_handling: If the category cannot be determined from the description alone, set category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Processes an entire CSV file of citizen complaints and writes the classified results to a new CSV file.
    input: Path to the input CSV file.
    output: Path to the generated output CSV file.
    error_handling: Logs errors for missing files or malformed CSV rows and skips processing for those entries.
