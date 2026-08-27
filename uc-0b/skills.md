skills:
  - name: retrieve_policy
    description: Load the .txt policy file and return the content as structured numbered sections.
    input: File path to the policy document (string).
    output: Dictionary mapping clause numbers to their text strings.
    error_handling: Raise an error if the file cannot be read or is completely malformed.
    
  - name: summarize_policy
    description: Take structured sections and produce a compliant summary with clause references.
    input: Dictionary of structured policy sections.
    output: A single string containing the compliant summary with all required clauses and conditions preserved.
    error_handling: Quote a clause verbatim and flag it if there is risk of meaning loss or scope bleed.
