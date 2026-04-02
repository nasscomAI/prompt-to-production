skills:
  - name: retrieve_policy
    description: Loads .txt policy file, returns content as structured numbered sections
    input: 
      type: string
      format: File path to the .txt policy document
    output: 
      type: dict
      format: Structured dictionary mapping numbered clauses (e.g., '2.3') to their text content
    error_handling: Raise an error and refuse execution if the file is missing, empty, or unreadable.

  - name: summarize_policy
    description: Takes structured sections, produces compliant summary with clause references
    input: 
      type: dict
      format: Structured sections produced by retrieve_policy
    output: 
      type: string
      format: Compliant summary text mapping every clause to its summarized meaning
    error_handling: If a clause cannot be safely summarized without meaning loss or matches a failure mode, quote it verbatim and flag it.
