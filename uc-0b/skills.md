skills:
  - name: retrieve_policy
    description: Loads a text policy file and extracts all numbered sections and clauses into a structured dictionary mapping clause numbers to their content.
    input: str (absolute or relative file path to the policy document)
    output: dict (mapping of clause numbers as strings to their raw descriptions)
    error_handling: Raises FileNotFoundError if the file doesn't exist, and handles blank line blocks or missing numbered clauses gracefully.

  - name: summarize_policy
    description: Processes structured policy clauses, summarizing simple entitlements while preserving absolute verbs, quoting/flagging complex clauses verbatim, and formatting the output.
    input: dict (structured clauses from retrieve_policy)
    output: str (formatted multi-line text summarizing all clauses with references)
    error_handling: Asserts the presence of all required clauses (like 5.2 and 7.2) and refuses to summarize them, selecting verbatim quotation instead.
