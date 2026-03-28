skills:
  - name: retrieve_policy
    description: Loads a plain text policy file and structures its content into a list of numbered sections.
    input: File path to the policy document (string).
    output: A structured dictionary or list where each item represents a parsed, numbered section/clause.
    error_handling: Raises a FileNotFoundError if the document is missing. If parsing fails, returns the raw text with a warning flag.

  - name: summarize_policy
    description: Summarizes the structured policy sections into a compliant summary that strictly preserves all multi-condition clauses.
    input: The structured clauses/sections from the policy document.
    output: A final summary text mapping directly back to the clause numbers without skipping any.
    error_handling: Fails or flags output if the LLM attempts to omit a numbered clause from its summary.
