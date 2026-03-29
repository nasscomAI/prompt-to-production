skills:
  - name: Sensitivity_Scanner
    description: Analyzes text for the presence of Personal Identifiable Information (PII) like credit card numbers or passwords.
    input: Raw text string from user input.
    output: Boolean value (True if PII is found, False if clean).
    error_handling: If the input is empty or null, it defaults to True (safety-first) and triggers a refusal.

  - name: Policy_Classifier
    description: Maps the user's intent against a list of blocked topics such as hacking, medical advice, or political discourse.
    input: User query string.
    output: Category label (e.g., 'Safe', 'Security_Violation', or 'Out_of_Scope').
    error_handling: When an intent is ambiguous, it flags the input for manual review and returns 'BLOCKED: NEUTRAL_UNCERTAINTY'.

  - name: Response_Gatekeeper
    description: Final validation step that ensures the system only outputs approved status codes.
    input: Categorized intent and PII scan result.
    output: Formatted string ('PROCEED' or 'BLOCKED').
    error_handling: If the internal logic fails, it defaults to 'BLOCKED' to ensure zero leakage of unsafe content.