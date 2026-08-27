skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: Filepath string pointing to the policy document (.txt).
    output: A dictionary mapping clause numbers to their full text.
    error_handling: Return an empty dictionary if the file cannot be parsed or found.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: A dictionary of structured policy clauses.
    output: A formatted string containing the summarized policy.
    error_handling: Ensure that no conditions are dropped during summarization. If a clause is complex, quote it verbatim.
