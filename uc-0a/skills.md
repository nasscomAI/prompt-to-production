# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: One complaint row in -> category + priority + reason + flag out.
    input: Dictionary representing a single complaint row with its description.
    output: Dictionary with keys: category, priority, reason, flag.
    error_handling: Return category "Other" and flag "NEEDS_REVIEW" if input is unparsable.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint per row, writes output CSV.
    input: String path to input CSV file.
    output: String path to output CSV file, writes the file to disk.
    error_handling: Flags nulls, does not crash on bad rows, produces output even if some rows fail.
