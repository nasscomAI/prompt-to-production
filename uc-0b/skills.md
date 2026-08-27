skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: A string representing the file path to the .txt policy document.
    output: A structured list or object containing the numbered clauses and their text.
    error_handling: Returns an error message if the file cannot be found, read, or parsed.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: A structured list or object containing the numbered clauses from the policy.
    output: A string containing the final constructed summary, preserving all original meaning.
    error_handling: Fails and returns an error if the input is empty or malformed.
