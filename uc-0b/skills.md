skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and parses it into structured sections and individual numbered clauses.
    input: File path string pointing to the source policy text file.
    output: List of structured clause dictionaries containing section_title, clause_id, and raw_text.
    error_handling: Raises FileNotFoundError if file is missing; raises ValueError if no valid numbered clauses can be parsed.

  - name: summarize_policy
    description: Generates a high-fidelity summary from structured clauses, preserving all obligations, multi-party approvers, numbers, and deadlines.
    input: List of structured clause dictionaries.
    output: Formatted string summary organized by section, including clause reference numbers, exact binding verbs, and explicit condition checks.
    error_handling: Flags clauses requiring verbatim quotation; enforces that multi-condition clauses retain all required entities before returning output.
