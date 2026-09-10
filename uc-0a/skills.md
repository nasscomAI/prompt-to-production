# UC-0A Complaint Classifier Skills

skills:

  - name: classify_complaint
    description: Classifies a citizen complaint into the correct category and priority.
    input: A single complaint description as text.
    output: Category, priority, reason, and flag for the complaint.
    error_handling: If the complaint is ambiguous, use the Other category and set the flag to NEEDS_REVIEW.

  - name: generate_reason
    description: Generates a short reason based only on evidence in the complaint description.
    input: Complaint description and its classification as text.
    output: One concise sentence explaining the classification using evidence from the complaint.
    error_handling: If there is insufficient information, provide a cautious reason based only on the available complaint text.
