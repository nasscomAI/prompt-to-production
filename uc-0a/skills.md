skills:
  - name: classify_complaint
    description: Analyzes one complaint description taking into account category, urgency keywords, and justification.
    input: dictionary representing a CSV row with a 'description' key
    output: dictionary adding 'category', 'priority', 'reason', and 'flag' keys to the original structure.
    error_handling: Return Other and NEEDS_REVIEW if description text is missing or incomprehensibly ambiguous.

  - name: batch_classify
    description: Streamlines processing of CSV complaint rows by calling classify_complaint iteratively safely.
    input: string file paths for input and output CSVs
    output: Writes parsed elements accurately to the target file.
    error_handling: Skip malformed rows safely.
