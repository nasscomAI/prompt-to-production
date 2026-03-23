skills:
  - name: complaint_text_analysis
    description: Analyse complaint description text and detect civic issue keywords.
    input: Complaint description string.
    output: Extracted keywords indicating issue type.
    error_handling: If description is empty, return NEEDS_REVIEW flag.

  - name: classify_complaint
    description: Assign category and priority based on detected keywords.
    input: Complaint description text.
    output: Category, priority and reason fields.
    error_handling: If no keyword is found, return category Other.