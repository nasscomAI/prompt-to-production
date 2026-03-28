skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections for processing.
    input: File path to the policy .txt file (string).
    output: A dictionary or list of structured sections, where each section has a number (e.g., '2.3') and content (string).
    error_handling: If the file does not exist or is not readable, raise a FileNotFoundError. If the file format is invalid (not .txt or malformed), return an empty structure and log a warning. For failure modes like clause omission, ensure all sections are extracted without skipping.

  - name: summarize_policy
    description: Takes structured policy sections and generates a compliant summary that preserves all obligations and conditions.
    input: Structured sections (dictionary or list as output from retrieve_policy).
    output: A string containing the summary text with clause references.
    error_handling: If input is invalid or empty, return an error message. For ambiguous sections matching failure modes (clause omission, scope bleed, obligation softening), enforce inclusion of all clauses, prevent addition of external info, and preserve exact conditions — if unable, quote verbatim and flag.
