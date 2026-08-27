skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path to the .txt policy document.
    output: A dictionary mapping section numbers to lists of clause texts.
    error_handling: Raise an exception if the file cannot be found or read. Return an empty structure if the file format is unrecognizable.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that retains all binding obligations with clause references.
    input: A dictionary of structured policy sections.
    output: A formatted string containing the summarized policy.
    error_handling: If a clause's meaning is ambiguous when shortened or if shortening would drop a condition, quote the clause verbatim and flag it with '[VERBATIM]'.
