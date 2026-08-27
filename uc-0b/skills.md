skills:
  - name: retrieve_policy
    description: Loads the policy text file and parses its contents into a dictionary of structured numbered sections and clauses.
    input: The path to the policy text file (string).
    output: A dictionary mapping clause numbers (strings, e.g., '2.3', '5.2') to their raw clause text content (strings).
    error_handling: If the file is missing, empty, or not a CMC HR leave policy document, it raises an appropriate error or returns an error message.

  - name: summarize_policy
    description: Summarizes the parsed policy sections clause-by-clause, ensuring all conditions are preserved and no external scope is added.
    input: A dictionary mapping clause numbers (strings) to their text content (strings).
    output: A string containing the final clause-by-clause summary, with verbatim quotes and flags for any clauses summarized with potential meaning loss.
    error_handling: If a clause cannot be summarized without altering or softening its obligations, it is quoted verbatim and flagged with '[VERBATIM_QUOTE]'.

