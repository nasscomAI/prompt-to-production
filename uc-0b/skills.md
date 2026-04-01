skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: String representing the absolute or relative path to the .txt policy file.
    output: Structured JSON or objects containing numbered sections and their corresponding text.
    error_handling: Return an explicit error if the file cannot be found, read, or if the format doesn't contain numbered sections.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured JSON or objects representing numbered sections from the policy.
    output: A compiled Markdown or text summary preserving all clauses and conditions with references.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it. Return explicit failure if any input sections fail to map to the summary output.
