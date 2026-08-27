# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a plain text policy file from the given path and parses its content into structured, numbered sections.
    input: A string representing the file path to the `.txt` policy document.
    output: A structured object (e.g., dictionary or list) where keys/indices are clause numbers and values are the exact text of those clauses.
    error_handling: If the file is missing, unreadable, or improperly formatted, aborts operation and raises a FileNotFoundError or ValueError.

  - name: summarize_policy
    description: Takes the structured policy sections and produces a compliant, concise summary that explicitly references clause numbers and preserves all multi-party obligations.
    input: The structured sections outputted by the `retrieve_policy` skill.
    output: A string containing the final summary text with all original numbered clauses represented.
    error_handling: If a clause cannot be summarized without softening its language or omitting a condition, outputs the clause verbatim and appends a `[NEEDS_REVIEW]` flag.
