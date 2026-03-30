# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single constituent complaint based on strict taxonomies and severity parameters.
    input: Dictionary with complaint details (e.g. description)
    output: Dictionary containing category, priority, reason, and flag
    error_handling: Return category: Other, flag: NEEDS_REVIEW if data is incomplete or ambiguous.

  - name: batch_classify
    description: Reads an input CSV containing multiple complaints, iterates via classify_complaint, and writes outputs to a new CSV.
    input: String path to input CSV file, String path to output CSV file
    output: A CSV file written to the output path
    error_handling: Skips rows that fail to be read, but continues execution. Warns on empty descriptions.
