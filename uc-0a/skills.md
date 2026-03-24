# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

sskills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A dictionary containing complaint text.
    output: A dictionary with category, priority, reason, and flag.
    error_handling: Returns category Other and flag NEEDS_REVIEW if input is invalid.

  - name: batch_classify
    description: Processes a CSV file and classifies all complaints.
    input: CSV file path.
    output: CSV file with classification results.
    error_handling: Handles row-level errors and continues processing.
