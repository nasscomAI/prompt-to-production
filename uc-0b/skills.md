# skills.md

skills:
  - name: retrieve_policy
    description: Load the leave policy text file and parse it into structured numbered sections for easier extraction.
    input: Path to the input policy text file.
    output: A dictionary mapping clause numbers to their exact text content.
    error_handling: Raises FileNotFoundError if the file doesn't exist, and handles unexpected formatting.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that covers all required clauses without dropping conditions.
    input: Dictionary mapping clause numbers to text content.
    output: A summarized text file containing the exact obligations and conditions of the key clauses.
    error_handling: If a clause's conditions are too complex to summarize without meaning loss, it quotes the clause verbatim.
