skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes every numbered clause by document name and section number.
    input: None; reads the three files from ../data/policy-documents.
    output: List of clauses with document, section, text and search terms.
    error_handling: A missing or unreadable file, or a file with no clauses, stops with a clear error message.

  - name: answer_question
    description: Finds the best-matching clauses in one document and returns them with citations, or the refusal template.
    input: question (str) and the clause index.
    output: Clause text with [document, section] citations from a single document, or the refusal template.
    error_handling: A score below the minimum returns the refusal template. Clauses from a second document are never added.