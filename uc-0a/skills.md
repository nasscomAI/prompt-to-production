# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a civic complaint into a predefined category and assigns priority.
    input: Complaint description (string) from CSV row.
    output: Category (string), Priority (string), Reason (string) in CSV format.
    error_handling: If description is ambiguous or does not match any category, outputs category: Other and flag: NEEDS_REVIEW.

  - name: extract_reason
    description: Extracts specific keywords from the complaint description to justify classification and priority.
    input: Complaint description (string).
    output: Reason (string) citing exact words from description.
    error_handling: If no relevant keywords found, outputs reason: No specific keywords found.
