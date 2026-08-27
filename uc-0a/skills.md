skills:
  - name: classify_complaint
    description: Iterates through a singular citizen complaint string and categorizes it based on strict operational rules.
    input: A raw complaint string containing the public description.
    output: A standardized record mapping to four distinct fields (category, priority, reason, flag).
    error_handling: Handles ambiguous or unidentifiable domains by forcefully setting the category to 'Other' and appending the 'NEEDS_REVIEW' flag.

  - name: batch_classify
    description: Iterates over an entire input CSV of row-level complaints and applies the classify_complaint skill recursively to generate a structured output CSV file.
    input: Path to the input CSV file containing sequential complaint rows without pre-assigned categories or priorities.
    output: Generates a resulting CSV file alongside the respective rows updated with category, priority, reason, and flag columns.
    error_handling: Skips or logs malformed rows independently without breaking the remaining batch's classification pass.
