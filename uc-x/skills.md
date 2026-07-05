# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes them by document name and section/clause numbers.
    input: None (loads from predefined paths in data/policy-documents/).
    output: A dictionary mapping document filenames to their structured sections and clauses.
    error_handling: Logs an error and exits if any of the three policy files are missing.

  - name: answer_question
    description: Searches the indexed document sections to find the single relevant clause that answers the user's question, returning the exact clause text with citation. If no match is found or if the question is out of scope, returns the exact refusal template.
    input: User question (string).
    output: A dictionary with keys — answer (string) and citation (string), or the refusal template.
    error_handling: Prevents cross-document blending by restricting the search to a single source document. If multiple documents match with equal weight, defaults to refusal or returns only the IT policy answer for personal devices.
