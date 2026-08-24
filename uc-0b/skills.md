skills:
  - name: retrieve_policy
    description: Loads a plain text policy file from disk and parses it into structured numbered sections and clauses.
    input: File path to plain text policy document (input_path).
    output: Structured dictionary mapping section titles and clause numbers to clause content.
    error_handling: Handles missing files or invalid formatting gracefully by throwing descriptive errors or returning empty structures.

  - name: summarize_policy
    description: Takes structured numbered policy clauses and generates a section-by-section summary ensuring 100% clause coverage and preserving all conditions.
    input: Structured policy clause dictionary or list.
    output: Plain text summary string formatted section by section with explicit clause citations.
    error_handling: Detects missing clause numbers or condition drops and quotes unsummarizable clauses verbatim with a warning flag.
