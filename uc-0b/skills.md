skills:
  - name: retrieve_policy
    description: "loads .txt policy file, returns content as structured numbered sections"
    input: "file path to the HR policy (.txt)"
    output: "structured text broken down into numbered sections and clauses"
    error_handling: "If the file is unreadable or empty, halt and report the error."

  - name: summarize_policy
    description: "takes structured sections, produces compliant summary with clause references"
    input: "structured numbered sections from retrieve_policy"
    output: "text string containing the final compliant summary with clear clause references"
    error_handling: "If summarising a clause causes multi-condition logic to drop or meaning loss (e.g. dropping HR Director from clause 5.2), quote the clause verbatim and flag it instead of summarising."
