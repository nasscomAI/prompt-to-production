# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint into a category, assigns priority, and provides a justification reason.
    input: Dictionary row containing complaint details.
    output: Dictionary containing category, priority, reason, and flag.
    error_handling: If input format is invalid, return None. If text is ambiguous, output category 'Other' and flag 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV containing complaints, categorizes each, and writes them to an output CSV.
    input: String path to input CSV, String path to output CSV.
    output: CSV file written to the output path.
    error_handling: Must flag nulls, not crash on bad rows, and successfully process and output valid rows even if some fail.
