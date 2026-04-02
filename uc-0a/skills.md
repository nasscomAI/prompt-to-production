# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_category
    description: Maps a citizen complaint description to a fixed taxonomy of categories.
    input: A string containing the raw complaint description.
    output: A string containing exactly one of the allowed categories (e.g., Pothole, Flooding, Other).
    error_handling: If the text is genuinely ambiguous or does not fit any specific category, outputs 'Other' and flags for review.

  - name: evaluate_priority
    description: Assesses the urgency of a complaint based on specific severity triggers and keywords like injury or hazard.
    input: A string containing the raw complaint description.
    output: A string indicating the priority level (Urgent, Standard, Low).
    error_handling: If no specific severity triggers are matched or context is missing, defaults to Standard or Low based on the category.

  - name: extract_justification
    description: Formulates exactly one sentence citing specific words from the description to justify the classification.
    input: A string containing the raw complaint description.
    output: A string containing a one-sentence reason.
    error_handling: If the description is extremely brief or lacks context, uses the exact text provided as the justification.
