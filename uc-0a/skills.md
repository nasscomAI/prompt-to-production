# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Takes one complaint row and returns category, priority, reason and flag.
    input: A dict with keys — complaint_id, description (string)
    output: A dict with keys — complaint_id, category, priority, reason, flag
    error_handling: If description is empty or unreadable, return category=Other, flag=NEEDS_REVIEW

  - name: batch_classify
    description: Reads the input CSV, applies classify_complaint per row, writes output CSV.
    input: input_path (string), output_path (string)
    output: CSV file with columns — complaint_id, category, priority, reason, flag
    error_handling: If a row fails, log the error and write flag=NEEDS_REVIEW for that row
