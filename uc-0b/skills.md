skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured, numbered sections.
    input: File path string pointing to the policy document (e.g., '../data/policy-documents/policy_hr_leave.txt').
    output: A dictionary or structured object mapping clause numbers (e.g., '2.3') to their exact text content.
    error_handling: If the file is not found or is unreadable, throw a FileNotFoundError with a clear message. If a clause number cannot be parsed, flag it for manual review.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary with explicit clause references, ensuring no conditions are dropped.
    input: The structured dictionary object outputted by retrieve_policy.
    output: A formatted string containing the 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) extracted verbatim.
    error_handling: If any of the 10 mandatory clauses are missing from the input, raise a MissingClauseError. Do not guess or hallucinate missing text.
