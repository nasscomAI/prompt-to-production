skills:
  - name: retrieve_policy
    description: Loads a plain text policy document and parses its content into structured numbered sections and clauses.
    input: File path to a plain text policy document (string, .txt format).
    output: List of structured clause objects, each containing clause number, section header, and raw clause text.
    error_handling: If the file is missing, empty, unreadable, or lacks standard numbered sections, raises an error and halts execution to prevent clause omission.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references while preserving all binding obligations and conditions.
    input: List of structured clause objects containing clause numbers and source text.
    output: Formatted plain text summary (string) with explicit clause references, preserved binding verbs, and complete multi-condition obligations.
    error_handling: If a clause cannot be condensed without loss of meaning or softening binding verbs, quotes the clause verbatim and flags it; if scope bleed or condition dropping is detected, halts and flags the section for manual review.
