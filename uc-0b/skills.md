# skills.md

skills:
  - name: retrieve_policy
    description: Loads a raw .txt policy file and parses its content into structured numbered sections.
    input: A string representing the file path to the policy document.
    output: A structured object (e.g., dictionary) mapping clause numbers to their exact text content.
    error_handling: If the file cannot be found or the format is unreadable, raise a clear file-loading error.

  - name: summarize_policy
    description: Takes the structured sections of the policy and produces a compliant summary that explicitly references each clause.
    input: The structured object of numbered sections returned by retrieve_policy.
    output: A text summary containing all clauses, preserving all conditions, with explicit clause references.
    error_handling: If any clause is missing from the generated summary, or if multi-condition obligations are dropped, flag the output or return an error citing the dropped conditions.
