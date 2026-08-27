# skills.md - UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns its content as structured, numbered sections.
    input: File path string to the policy text file.
    output: Structured representation mapping section numbers to clause text.
    error_handling: Refuses to proceed and alerts the user if the file cannot be read or is missing numbered formatting.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with explicit clause references.
    input: Structured policy sections dictionary or object.
    output: A summary text document string containing all clauses with their exact conditions preserved.
    error_handling: Flags clauses that cannot be safely summarized without meaning loss and outputs them verbatim in the summary.
