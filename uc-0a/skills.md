# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category, priority, and justification.
    input: A dictionary representing a single CSV row, containing at least the key 'description'.
    output: A dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is missing, null, or empty, return category: 'Other', priority: 'Standard', reason: 'Missing description', and flag: 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV file of complaints, applies classify_complaint to each row, and writes the results to a new CSV.
    input: input_path (string) for the source CSV and output_path (string) for the destination CSV.
    output: None. The function writes results directly to the specified output_path.
    error_handling: Must flag null values, continue processing if a single row fails, and ensure the output file is valid even if some rows contain errors.
