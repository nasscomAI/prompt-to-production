skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and parses the content into structured numbered sections.
    input: File path (string) referencing a valid .txt document.
    output: Structured mapping (dict/list) containing section numbers, clause numbers, and raw text.
    error_handling: Raises FileNotFoundError if path does not exist; raises ValueError if file is empty or lacks numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and generates a strict, meaning-preserving summary with explicit clause references.
    input: Structured policy sections (dict/list).
    output: Formatted string containing clause-by-clause summaries preserving all obligations and conditions.
    error_handling: Quotes clauses verbatim if condensation causes condition dropping, clause omission, or scope bleed.