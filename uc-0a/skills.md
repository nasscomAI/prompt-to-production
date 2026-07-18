# skills.md

skills:
  - name: classify_complaint
    description: Classifies one complaint row into the required schema by choosing an allowed category, priority, reason, and flag.
    input: A single complaint row containing at least a description field.
    output: A structured classification object with category, priority, reason, and flag.
    error_handling: If the description is missing or too ambiguous to classify confidently, return category Other and flag NEEDS_REVIEW rather than guessing.

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the classified output CSV.
    input: An input CSV path and an output CSV path.
    output: A written CSV containing one row per complaint with category, priority, reason, and flag.
    error_handling: If the input file is missing or invalid, return a clear file error and stop before writing output.
