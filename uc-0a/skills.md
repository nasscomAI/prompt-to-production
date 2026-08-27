# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dictionary representing a single complaint row with fields like `description`.
    output: A dictionary with keys: `complaint_id`, `category`, `priority`, `reason`, `flag`.
    error_handling: Returns `category: Other` and `flag: NEEDS_REVIEW` if input is ambiguous or invalid.

  - name: batch_classify
    description: Processes an input CSV file, applies `classify_complaint` to each row, and writes the results to an output CSV.
    input: File paths for input CSV and output CSV.
    output: A CSV file with classified rows including `category`, `priority`, `reason`, and `flag`.
    error_handling: Skips invalid rows, logs errors, and ensures the output file is written even if some rows are problematic.
