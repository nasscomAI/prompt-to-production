skills:
  - name: analyze_complaint_text
    description: Analyzes the text of a citizen complaint and assigns category and priority based on specific trigger words.
    input: Dictionary containing the original row data (e.g., complaint_id, description).
    output: Dictionary with the parsed "category", "priority", "reason", and "flag".
    error_handling: If the input is null or ambiguous, returns category "Other" and flag "NEEDS_REVIEW".
