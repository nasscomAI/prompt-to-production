skills:
  - name: classify_complaint
    description: Classifies a single complaint row by mapping its description to category, priority, reason, and flag.
    input: row (dictionary containing complaint fields like description and days_open).
    output: classification (dictionary with keys category, priority, reason, flag).
    error_handling: If description is missing or empty, sets category to Other, priority to Standard, reason to Empty description, and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads complaints from a CSV file, classifies each row, and writes the results to an output CSV file.
    input: input_path (string) - Path to input CSV, output_path (string) - Path to output CSV.
    output: None (writes results file).
    error_handling: If the input file is missing, prints an error to stderr and exits with a non-zero exit code.
