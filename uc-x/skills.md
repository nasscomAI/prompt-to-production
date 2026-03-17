skills:
  - name: retrieve_documents
    description: Loads and indexes all company policy documents by document name and section number.
    input: List of file paths to policy text files (string array)
    output: Dictionary mapping document name → section number → section text
    error_handling: Raises error if any file is missing, empty, or sections cannot be parsed.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with citation or refusal template.
    input: 
      - indexed_documents (dict from retrieve_documents)
      - question (string)
    output: Dictionary with:
      - answer (string)
      - citation (document name + section) OR refusal template
    error_handling: 
      - If question not found in any document, return refusal template exactly
      - If multiple documents contain partial answers, refuse rather than blend