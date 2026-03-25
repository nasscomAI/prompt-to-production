skills:
  - name: classify_complaint
    description: Analyzes the text of a citizen complaint and assigns it to a standard infrastructure category with an appropriate priority level.
    input: String containing the raw text of the citizen complaint.
    output: JSON object containing 'category' (string), 'priority' (string), and 'reason' (string).
    error_handling: Returns {"category": "Other", "priority": "Low", "reason": "Unrecognized or unparseable input text.", "flag": "NEEDS_REVIEW"} when input is invalid or ambiguous.

  - name: detect_urgency_keywords
    description: Scans a text for sensitive or urgency-indicating keywords to recommend immediate escalation.
    input: String containing the raw text of the complaint.
    output: Boolean indicating whether urgency keywords are present, and a list of the matching keywords.
    error_handling: Returns false and an empty list if the input is empty or non-text.
