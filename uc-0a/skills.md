# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: extract_complaint
    description: Extracts and normalizes the text of a citizen complaint for classification.
    input: Raw complaint description text (string).
    output: Cleaned complaint text (string) ready for classification.
    error_handling: If input is empty, non-text, or ambiguous, return an error message "INVALID_INPUT" and skip classification.

  - name: classify_complaint
    description: Classifies the complaint into a category and priority, citing reasons.
    input: Complaint text (string) from extract_complaint.
    output: Structured record with fields: category (string), priority (string), reason (string).
    error_handling: If category cannot be determined from description alone, set category to "Other", add flag "NEEDS_REVIEW", and provide reason citing the uncertainty.
