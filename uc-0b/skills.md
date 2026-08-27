# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns the content as structured, numbered sections.
    input: Path to the .txt policy file.
    output: A list of structured, numbered sections/clauses.
    error_handling: Raises an error and alerts the user if the file cannot be read or parsed properly.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: List of structured sections from the policy document.
    output: A text summary string preserving all conditions and numbered clauses.
    error_handling: Quotes the clause verbatim and flags it if summarizing it accurately is not possible without meaning loss.
