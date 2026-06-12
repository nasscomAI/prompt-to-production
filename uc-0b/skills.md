skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered sections.
    input: Path to the policy text file (string).
    output: A dictionary mapping clause numbers/headers (strings) to their corresponding text content (strings).
    error_handling: Raises an error if the file is missing or empty, or returns a warning if sections cannot be parsed.

  - name: summarize_policy
    description: Summarizes the parsed policy sections, ensuring all required clauses are represented and no conditions are dropped.
    input: A dictionary of structured policy sections mapping clause numbers to text.
    output: A string containing the formatted summary, listing all mapped clauses and verbatim quotes for complex sections.
    error_handling: If a clause cannot be summarized without losing meaning or dropping conditions, quotes the clause verbatim and adds a warning tag.
