# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint into category, priority, reason, and flag.
    input: complaint_text
    output: category, priority, reason, flag

  - name: batch_classify
    description: >
      Reads CSV file and applies classification to each row.
    input: csv_file
    output: classified_csv