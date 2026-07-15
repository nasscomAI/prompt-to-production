# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category and priority with reasoning.
    input: Dictionary containing complaint fields (complaint_id, description, days_open, etc.)
    output: Dictionary with keys {category, priority, reason, flag} where category is one of 10 allowed values, priority is Urgent/Standard/Low, reason cites specific description words, flag is NEEDS_REVIEW or empty.
    error_handling: If description is missing or empty, return category='Other', flag='NEEDS_REVIEW'. If severity keywords present but category ambiguous, priority still becomes Urgent.

  - name: detect_severity_keywords
    description: Scans complaint description for any of the 9 severity keywords that trigger Urgent priority.
    input: String containing complaint description text.
    output: Boolean (True if any severity keyword found) and list of matched keywords.
    error_handling: Returns False and empty list if description is None or empty string.

  - name: map_to_category
    description: Maps complaint description to exactly one of the 10 allowed categories using keyword matching.
    input: String containing complaint description text.
    output: String - one of the 10 exact category names, or 'Other' if no clear match.
    error_handling: Returns 'Other' if description is ambiguous or doesn't match any category pattern clearly.

  - name: generate_reason
    description: Generates a reason field citing specific words from the complaint description.
    input: Complaint description (string), assigned category (string), assigned priority (string), matched keywords (list).
    output: String - one sentence explaining classification with quoted words from description.
    error_handling: If description is empty, returns generic reason stating insufficient information.

  - name: batch_classify
    description: Reads input CSV, applies classify_complaint to each row, writes output CSV.
    input: Path to input CSV file containing complaints.
    output: Writes CSV file with columns: complaint_id, category, priority, reason, flag.
    error_handling: If input file not found, raises FileNotFoundError with clear message. If CSV malformed, reports line number of error.
