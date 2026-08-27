# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and determines its exact category, severity priority, reasoning, and any ambiguity flags.
    input: A dictionary representing a single CSV row with at least 'complaint_id' and 'description'.
    output: A dictionary with keys (complaint_id, category, priority, reason, flag).
    error_handling: If input data is missing a description, set category to 'Other', flag to 'NEEDS_REVIEW', and note it in the reason.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints, applies the classify_complaint skill to each row, and safely writes the results to an output CSV.
    input: input_path (string) and output_path (string).
    output: Writes a CSV file to output_path.
    error_handling: Skips malformed rows without crashing the process, ensuring all successfully processed rows are safely written to the output file.
