skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path to a .txt policy document.
    output: Structured text representing the policy, parsed into numbered sections.
    error_handling: Return an error if the file is missing, cannot be read, or cannot be parsed into sections.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections of the policy.
    output: Compliant text summary that maps correctly to the given clauses.
    error_handling: Return an error if the input lacks structured sections or if a clause definition is malformed.
