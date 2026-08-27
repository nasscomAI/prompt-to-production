# skills.md

skills:
  - name: retrieve_policy
    description: Loads a strictly defined .txt policy file and returns its content as structured, numbered sections.
    input: File path to the policy document (e.g., .txt format).
    output: A structured object or text block parsing the document into distinct, numbered clauses.
    error_handling: Refuse to proceed and raise an error if the file is missing, empty, or lacks readable numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant, complete summary with clause references.
    input: A list of structured, numbered clauses retrieved from the policy.
    output: A comprehensive summary text document ensuring no clause or multi-condition obligation is omitted.
    error_handling: If a clause is deemed completely summarize-proof without altering meaning, the system must quote it verbatim and flag it in the output instead of attempting a summary.
