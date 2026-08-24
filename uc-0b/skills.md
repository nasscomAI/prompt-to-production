skills:
  - name: retrieve_policy
    description: Loads .txt policy file and returns content as structured numbered sections.
    input: string (file path to the input policy document)
    output: dictionary mapping section numbers to their text content.
    error_handling: Raise an error if the file cannot be read or is not found.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: dictionary mapping section numbers to text content.
    output: string (the final compliant summary text).
    error_handling: Fail or raise an error if a clause cannot be extracted cleanly or meaning might be lost without exact quoting.
