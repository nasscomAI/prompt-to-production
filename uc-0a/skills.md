skills:
  - name: parse_civic_complaint
    description: Analyzes the text of a civic complaint to determine its category, priority, reason, and flag review status.
    input: Dictionary row representing a single complaint containing a 'description' string field.
    output: Dictionary with keys 'complaint_id' (string or int), 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string or None).
    error_handling: Returns category as 'ERROR', priority as 'ERROR', and flag as 'PROCESSING_ERROR' if the row causes an unhandled exception. Returns 'Other' category and 'NEEDS_REVIEW' flag if description is empty or unclear.
