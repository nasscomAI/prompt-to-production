skills:
  - name: classify_complaint
    description: Takes one complaint row as input and returns category, priority, reason, and flag.
    input: Dictionary representing a single citizen complaint row.
    output: Dictionary containing category (string), priority (string), reason (string), and flag (string).
    error_handling: In cases of genuine ambiguity or missing attributes, outputs category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV file, applies the classify_complaint skill to every row, and writes the results to an output CSV file.
    input: Path to an input CSV file (e.g., test_pune.csv).
    output: Path to an output CSV file (e.g., results_pune.csv).
    error_handling: Guarantees that the output CSV contains exactly as many results as the input rows, using fallback 'Other' values if processing fails.
