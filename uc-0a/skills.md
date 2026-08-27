# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine standardized category, priority, and extracted reason.
    input: Dictionary containing a single record from the CSV with keys `complaint_id`, `description`, etc.
    output: Dictionary with strings for keys `category`, `priority`, `reason`, and `flag`.
    error_handling: Return `"Other"` for category and `"NEEDS_REVIEW"` for flag if parsing or mapping fails.

  - name: batch_classify
    description: Iterates through all complaints in the input file safely, tracking errors and generating an output file.
    input: Two strings representing the file path of the input CSV and output CSV.
    output: None. Writes a CSV file directly to the provided output path.
    error_handling: Surrounds processing inside a try blocks to ensure safe completion even if a row is invalid or malformed.
