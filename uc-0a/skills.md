# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a category and priority based on its description.
    input: A dictionary representing a row from the complaint CSV (containing 'description').
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: If the description is empty or the category is ambiguous, it returns 'Other' for category and sets the 'NEEDS_REVIEW' flag.

  - name: batch_classify
    description: Processes a CSV file of complaints, applying the classify_complaint skill to each row and writing the results to an output CSV.
    input: Paths to the input CSV file and the desired output CSV file.
    output: None (writes to output file).
    error_handling: Continues processing if individual rows fail; flags null or empty rows.
