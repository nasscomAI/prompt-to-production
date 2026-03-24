# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document.
    output: List of dictionaries or a JSON object mapping section numbers to their full text.
    error_handling: If the file cannot be read or is corrupted, return an error object and stop processing.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that retains all conditions and includes clause references.
    input: Structured numbered sections of the policy.
    output: Formatted text summary with explicit clause citations (e.g., Clause 5.2).
    error_handling: If any structured section is missing required conditions or cannot be parsed, include the raw text with a '[REVIEW FAILED PARSE]' flag.
