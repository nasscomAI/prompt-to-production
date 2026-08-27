skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns its content parsed into structured, numbered sections.
    input: Path to the policy text file (string).
    output: A dictionary mapping clause numbers (e.g., "2.3") to their exact textual content (string).
    error_handling: If the file is not found or is in an unexpected format, raise a FileNotFoundError or ValueError.

  - name: summarize_policy
    description: Takes structured sections of a policy and produces a concise summary preserving all binding constraints and clause references.
    input: Structured sections mapping clause numbers to their content (dictionary).
    output: A compliant summary markdown string referencing the clause numbers and preserving all conditions and obligations.
    error_handling: If any clause cannot be summarized without loss of meaning, quote it verbatim and flag it.

