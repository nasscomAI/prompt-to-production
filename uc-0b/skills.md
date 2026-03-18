skills:
  - name: extract_clauses
    description: Splits complaint text into individual meaningful clauses.
    input: A string containing complaint text.
    output: A list of cleaned clause strings.
    error_handling: If text is empty or cannot be split, returns original text as a single clause and flags for review.

  - name: process_complaint
    description: Processes complaint text and ensures all clauses are extracted and validated.
    input: A string containing complaint text.
    output: A dictionary with list of clauses and optional flag.
    error_handling: If no valid clauses are found, returns original text with flag "NEEDS_REVIEW".
