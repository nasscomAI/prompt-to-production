# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies a civic complaint into one of the allowed categories and assigns a priority based on severity keywords.
    input: Complaint description as a string.
    output: Dictionary with fields: category (string), priority (string), reason (string), flag (string or blank).
    error_handling: If the category cannot be determined, sets category to 'Other' and flag to 'NEEDS_REVIEW'.

  - name: assign_priority
    description: Assigns priority to a complaint based on presence of severity keywords.
    input: Complaint description as a string.
    output: String: 'Urgent', 'Standard', or 'Low'.
    error_handling: Defaults to 'Standard' if no severity keywords are found and input is valid; raises error if input is empty or not a string.
