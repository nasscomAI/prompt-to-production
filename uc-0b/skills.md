# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured, numbered sections.
    input: A string representing the file path to the policy document (e.g., .txt).
    output: A JSON object mapping section numbers to their corresponding text content.
    error_handling: Raise a FileNotFoundError if the document cannot be located or read.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that retains all conditions and includes clause references.
    input: A JSON object of structured policy sections.
    output: A string containing the final summary, with explicit references to the original clause numbers.
    error_handling: If a clause cannot be summarized without altering its meaning, include the exact verbatim quote and append a [FLAG: NEEDS REVIEW] tag.
