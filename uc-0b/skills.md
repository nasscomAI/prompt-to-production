# skills.md — UC-0B Skills

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses its contents into structured numbered sections and clauses.
    input: Path to the .txt policy file (string).
    output: A list or mapping of structured clauses, each containing clause number, heading, and raw text.
    error_handling: If the file does not exist, cannot be read, or contains unparseable content, raise a descriptive FileNotFoundError or parsing error and log the missing sections.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that retains all numbered clauses, exact conditions, and binding verbs.
    input: Structured policy clauses/sections from retrieve_policy.
    output: Formatted summary text preserving clause numbers, full multi-condition obligations, and verbatim quotes for critical obligations.
    error_handling: If any clause cannot be summarized without loss of meaning, quote it verbatim and append a warning flag.

