# skills.md

skills:
  - name: classify_complaint
    description: Classifies a complaint description into a predefined category and assigns a priority.
    input: Complaint description (string)
    output: Dictionary with fields: category (string), priority (string), reason (string)
    error_handling: If the description is ambiguous or insufficient, returns category: Other and flag: NEEDS_REVIEW.

  - name: extract_keywords
    description: Extracts key words or phrases from the complaint description that justify the classification.
    input: Complaint description (string)
    output: List of strings (keywords/phrases)
    error_handling: Returns an empty list if no relevant keywords are found.