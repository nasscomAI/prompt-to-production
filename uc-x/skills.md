skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes them by document name and section number for precise retrieval.
    input: A list of file paths to the policy documents.
    output: A structured collection of document sections keyed by document name and section number.
    error_handling: If a file is missing or unreadable, return a clear error and stop rather than guessing.

  - name: answer_question
    description: Searches the indexed sections, returns a single-source answer with a document and section citation, or returns the exact refusal template.
    input: A natural-language question string.
    output: A plain-text answer containing either one cited policy section or the exact refusal template.
    error_handling: If multiple documents appear equally relevant, refuse instead of blending them into one answer.
