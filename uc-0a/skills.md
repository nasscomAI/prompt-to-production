skills:
  - name: classify_complaint
    description: Determines correct department category from complaint text.
    input: Complaint description string.
    output: Department category with explanation.
    error_handling: If classification unclear return Other with NEEDS_REVIEW.

  - name: extract_keywords
    description: Extracts important keywords from complaint text.
    input: Complaint description.
    output: List of detected keywords.
    error_handling: Return empty list if no keywords found.
