# skills.md

skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path string to the policy document
    output: Structured text with numbered sections and clauses
    error_handling: Return error if file not found or if format is not parseable as text

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured text with numbered sections
    output: Text summary of the policy explicitly referencing section numbers
    error_handling: Return error if the generated summary misses any input clauses or fails validation
