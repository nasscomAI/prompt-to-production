skills:
  - name: retrieve_policy
    description: Loads a raw .txt policy file and returns its content organized into structured, numbered sections.
    input: File path string pointing to a .txt policy document.
    output: A structured object mapping clause numbers to their exact verbatim text.
    error_handling: Return an explicit error if the file cannot be found, read, or if no numbered clauses can be detected.

  - name: summarize_policy
    description: Performs structural summarization of policy sections while ensuring zero meaning loss, actively preventing clause omission, scope bleed, and obligation softening.
    input: Structured sections containing clause numbers and their verbatim text.
    output: An exhaustive summary text with explicit clause references, strictly preserving every core obligation, binding verb, and multi-condition requirement.
    error_handling: If a clause cannot be summarized without meaning loss or dropping a condition, refuse to summarize it, quote it verbatim instead, and flag it.
