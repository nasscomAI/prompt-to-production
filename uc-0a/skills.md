skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a specific category, priority, reason, and flag.
    input: A dictionary containing the complaint data, specifically the text description.
    output: A dictionary with keys - complaint_id, category, priority, reason, flag.
    error_handling: If the complaint description is completely ambiguous, unreadable, or missing, output category as 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: Two strings representing the file paths - input_path (CSV) and output_path (CSV).
    output: Creates and writes a new CSV file at the output_path.
    error_handling: Flags null rows, catches exceptions to avoid crashing on bad rows, and ensures the output CSV is still produced for the successful rows.