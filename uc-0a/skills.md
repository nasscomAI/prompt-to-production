# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classify a single complaint row into `category`, `priority`, `reason`, and `flag` for UC-0A.
    input: A complaint object or row containing the description and any available fields from one test CSV row.
    output: A JSON object with fields `category`, `priority`, `reason`, and `flag`.
    error_handling: If the complaint is ambiguous or the category cannot be determined, return `category: Other`, set `flag: NEEDS_REVIEW`, and still provide a reason citing words from the input.

  - name: batch_classify
    description: Read an input test CSV, apply `classify_complaint` to each row, and write the results CSV.
    input: Input file path to a city test CSV and output file path for `results_[your-city].csv`.
    output: A CSV file with one classification row per input complaint, containing `category`, `priority`, `reason`, and `flag`.
    error_handling: If the input is missing or a row cannot be parsed, report the failure and skip invalid rows while preserving valid row order when possible.
