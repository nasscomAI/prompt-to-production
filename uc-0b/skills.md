skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input:  type: string format: file path to the text document 
    output:type: array format: list of objects containing section numbers and text content 
    error_handling: If the file is missing, unreadable, or not formatted with clear sections, halt execution and return a parse error instead of proceeding.

  - name: summarize_policy 
    description: Takes structured sections and produces a compliant summary with clause references. 
    input: type: array format: list of objects containing section numbers and text content 
    output: type: string format: plain text summary explicitly referencing clause numbers 
    error_handling: If summarizing a clause risks clause omission, scope bleed, or obligation softening (such as dropping one of multiple required conditions), quote the clause verbatim and flag it.
