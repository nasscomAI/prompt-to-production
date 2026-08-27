# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A dictionary containing complaint data (including 'description').
    output: A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: Return category 'Other' and flag 'NEEDS_REVIEW' if input is invalid or ambiguous.

  - name: batch_classify
    description: Reads a CSV of complaints, classifies each, and writes the results to a new CSV.
    input: Path to the input CSV file.
    output: Path to the output CSV file.
    error_handling: Flag nulls, do not crash on bad rows, and produce output even if some rows fail.
