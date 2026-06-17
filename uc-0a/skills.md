skills:
  - name: classify_complaint
    description: Classifies a single complaint row into one of the allowed categories and determines the priority based on severity keywords.
    input: A dictionary containing the keys 'complaint_id' and 'description'.
    output: A dictionary with keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is empty or null, it sets the category to 'Other', flag to 'NEEDS_REVIEW', and reason to 'Missing description'. If the category is ambiguous or multiple categories match, it flags the row for review and sets the category to 'Other'.

  - name: batch_classify
    description: Reads citizen complaints from an input CSV file, applies the classify_complaint skill to each row, and writes the output to a results CSV.
    input: The input CSV file path (string) and output CSV file path (string).
    output: None (writes results to the output CSV file).
    error_handling: Handles missing input files or formatting errors gracefully, logs warnings, and ensures the process completes even if individual rows have issues.
