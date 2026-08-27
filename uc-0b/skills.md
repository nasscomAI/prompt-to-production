# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain text policy document and parses it into structured sections and numbered clauses for precise analysis.
    input: Path to the .txt policy file.
    output: A dictionary or list of structured sections (e.g., {"2.3": "text", "2.4": "text"}).
    error_handling: Raises an error if the file is missing or if the numbering format is unrecognizable.

  - name: summarize_policy
    description: Generates a high-integrity summary that preserves all legal obligations and conditions, referencing every numbered clause in the source.
    input: Structured sections from retrieve_policy.
    output: A summary text file where every clause is accounted for and multi-part conditions are fully preserved.
    error_handling: If a clause is too complex to summarize without losing detail, it quotes the clause verbatim and adds a [COMPLEXITY_FLAG].
