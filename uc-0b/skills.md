skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured sections and numbered clauses.
    input: Absolute path to the policy text file.
    output: A structured representation of the clauses in the file.
    error_handling: Returns an empty list or raises a descriptive error if the file cannot be loaded.

  - name: summarize_policy
    description: Summarizes the structured clauses, ensuring all critical obligations are preserved and no conditions are softened.
    input: Structured policy sections or list of clauses.
    output: A string containing the compliant summary with verbatim quotes for critical clauses.
    error_handling: Refuses to summarize and quotes/flags any clause containing complex multi-conditions to prevent meaning loss.
