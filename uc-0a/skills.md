# skills.md

skills:
  - name: classify_complaint
    description: Takes one complaint row and classifies it into a strict category, assigns priority based on severity keywords, provides a reason, and flags ambiguity.
    input: A dictionary representing one complaint row with at least a description.
    output: A dictionary containing the exact category, priority, reason, and flag.
    error_handling: If the category cannot be determined from the description alone, outputs category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint per row, and writes the results to an output CSV.
    input: String file paths for the input CSV and output CSV.
    output: A CSV file written to the output path containing the classified rows.
    error_handling: Flags nulls, does not crash on bad rows, and ensures it produces an output CSV even if some rows fail.
