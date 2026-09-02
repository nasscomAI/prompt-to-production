# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into `category`, `priority`, `reason`, and `flag` according to the schema.
    input: A CSV row containing the complaint description (and any other required columns).
    output: An object with fields `category`, `priority`, `reason`, and `flag`.
    error_handling: If the category cannot be confidently determined, set `category` to `Other` and `flag` to `NEEDS_REVIEW`.

  - name: batch_classify
    description: Reads an input CSV, applies `classify_complaint` to each row, and writes an output CSV with classification fields.
    input: Paths to the input CSV file and the desired output CSV file.
    output: Output CSV file with added columns `category`, `priority`, `reason`, and `flag` for each row.
    error_handling: Rows that cause errors are logged and marked with `flag` = `NEEDS_REVIEW` in the output.

