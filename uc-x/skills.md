# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all policy files and indexes them by document name and section number.
    input: List of paths to policy document text files.
    output: Indexed key-value document store.
    error_handling: Logs a warning if a document is missing, unreadable, or cannot be indexed.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source answer with a citation, or the exact refusal template.
    input: A user-provided question string.
    output: Single-source answer string with exact section citation, or the standard refusal template.
    error_handling: Applies the exact predefined refusal template if the answer cannot be found completely within a single source document.
