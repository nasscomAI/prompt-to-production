# skills.md
# UC-0B — Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Reads the raw HR policy text file and parses it into structured numbered clauses.
    input: File path to policy document (string).
    output: List of structured clauses, each containing clause number and text.
    error_handling: If file is missing or unreadable, raise an error.

  - name: summarize_policy
    description: Takes structured clauses and generates a compliant summary without losing multi-condition obligations.
    input: List of structured clauses.
    output: A single string containing the summarized policy.
    error_handling: If a clause cannot be safely summarized without dropping conditions, it quotes the clause verbatim.
