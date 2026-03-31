skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: File path to the .txt policy document (string)
    output: List of dictionaries or structured objects representing numbered sections and content
    error_handling: Refuses to proceed if file is inaccessible or unreadable.

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured numbered sections from retrieve_policy
    output: String or text file content containing the compliant summary with precise clause references
    error_handling: Quotes clause verbatim and flags it if it cannot be summarized without omitting conditions or softening obligations.
