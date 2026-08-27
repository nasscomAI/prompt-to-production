skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and extracts its content into structured numbered sections.
    input: File path to the .txt policy document (String).
    output: Structured text containing the original content organized by numbered sections/clauses.
    error_handling: If the file is not found or unreadable, return an error indicating the loading failure. If the document cannot be parsed into sections, return a formatting error.

  - name: summarize_policy
    description: Takes structured sections of a policy document and produces a compliant summary with clause references.
    input: Structured policy content containing numbered sections/clauses.
    output: A verifiable text-based summary of the policy where every numbered clause is represented and multi-condition obligations are strictly preserved.
    error_handling: If a clause cannot be summarized without meaning loss, quote it verbatim and flag it in the output. If the input is empty or invalid, return an error requesting valid structured sections.
