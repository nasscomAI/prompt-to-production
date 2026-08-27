# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint to determine its category and priority based on its text description.
    input: A single dictionary representing one complaint row.
    output: A dictionary containing the keys category, priority, reason, and flag.
    error_handling: If the input is null or missing a description, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (string) for the input CSV, output_path (string) for the output CSV.
    output: A CSV file written to the output_path containing the classification results for all processed rows.
    error_handling: Flags nulls, skips or gracefully handles bad rows without crashing the process, and ensures an output file is produced even if some rows fail.
