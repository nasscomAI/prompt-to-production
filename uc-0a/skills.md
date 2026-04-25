# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and determines its category, priority, reasoning, and review flag.
    input: A single complaint row dictionary containing the description.
    output: A dictionary containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If input is invalid or ambiguous, return category "Other", priority "Low", flag "NEEDS_REVIEW", and reason stating the error.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (string) and output_path (string) representing file paths.
    output: Writes a CSV file to output_path.
    error_handling: Must flag nulls, not crash on bad rows, and produce output even if some rows fail to classify.
