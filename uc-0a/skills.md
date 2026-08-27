# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag based on defined rules.
    input: A dictionary representing one complaint row with fields like complaint_id and description.
    output: A dictionary containing complaint_id, category, priority, reason, and flag.
    error_handling: If description is missing or unclear, assigns category as "Other", sets flag to "NEEDS_REVIEW", and provides a fallback reason.

  - name: batch_classify
    description: Processes a CSV file of complaints and applies classification to each row.
    input: Input CSV file path containing complaint data.
    output: Output CSV file path with classified results for all complaints.
    error_handling: Skips or safely handles invalid rows, ensures output file is still generated, and flags problematic rows with "NEEDS_REVIEW".