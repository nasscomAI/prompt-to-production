skills:
  - name: classify_complaint
    description: Evaluates an incoming citizen complaint and correctly classifies it with a standardized category and priority level, along with a verifiable reason.
    input: Raw citizen complaint data, specifically the text provided in the complaint description.
    output: A classification result containing 'category', 'priority' (Urgent, Standard, or Low), a 'reason' field (exactly one sentence citing specific words), and a 'flag' field.
    error_handling: If the category cannot be confidently determined or is genuinely ambiguous based on the description alone, set the flag field to 'NEEDS_REVIEW' and category to 'Other'.
