# skills.md

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return the content as structured numbered sections.
    input: Path to the .txt policy file (string).
    output: Structured representation of numbered policy sections (e.g., dictionary or list of clauses).
    error_handling: Raise an error if the file is missing or unreadable. Skip unparseable sections.

  - name: summarize_policy
    description: Take structured policy sections and produce a compliant summary maintaining complete clause references and obligations.
    input: Structured representation of numbered policy sections.
    output: A compliant text summary referencing all clauses.
    error_handling: If a clause cannot be accurately summarized without meaning loss, quote it verbatim and flag it in the output instead.
