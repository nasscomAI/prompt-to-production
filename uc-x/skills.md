skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: Document file paths
    output: Indexed text separated by document name and section number.
    error_handling: Exits if the documents are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents, returning a single-source answer with citation OR the refusal template.
    input: Employee question (string)
    output: Single-source factual answer citing the exact source document name and section number, or the exact refusal template string.
    error_handling: Immediately uses the exact refusal template if the answer requires cross-document blending, hedging, or outside knowledge.
