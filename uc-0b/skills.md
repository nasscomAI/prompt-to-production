skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered sections.
    input:
      type: str
      format: Path to the policy document text file.
    output:
      type: dict
      format: A dictionary mapping clause numbers to their raw text contents.
    error_handling: Raises a FileNotFoundError if the path is invalid or empty.

  - name: summarize_policy
    description: Summarizes the parsed policy clauses, enforcing that all conditions, binding verbs, and specific clauses are preserved.
    input:
      type: dict
      format: A dictionary mapping clause numbers to raw texts.
    output:
      type: str
      format: The formatted summary string to write to output.
    error_handling: If any of the 10 target clauses are missing in the input dictionary, it flags them in the summary as missing from source.
