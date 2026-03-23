skills:
  - name: retrieve_policy
    description: loads .txt policy file, returns content as structured numbered sections
    input: String representing the absolute file path to the .txt policy document
    output: A structured object (e.g., list or dictionary) mapping clause numbers to text
    error_handling: Raises an error if the file is not found or is unreadable

  - name: summarize_policy
    description: takes structured sections, produces compliant summary with clause references
    input: Structured sections (e.g., list or dictionary mapping clause numbers to text)
    output: A compliant summary string highlighting core obligations without condition drops
    error_handling: Flags and quotes the clause verbatim if it cannot be summarized without loss of meaning
