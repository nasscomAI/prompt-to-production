skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: File path to the .txt policy document (string).
    output: Structured representation of the policy document with clearly delineated numbered sections.
    error_handling: Returns an error message if the file cannot be read, does not exist, or does not contain decipherable numbered sections.

  - name: summarize_policy
    description: Takes structured sections of a policy document and produces a compliant summary with clause references.
    input: Structured policy content (numbered sections).
    output: A concise and comprehensive summary referencing the original clause numbers.
    error_handling: Fails safely and alerts the user if conditions in a clause are ambiguous or if a clause cannot be summarized without losing original meaning.
