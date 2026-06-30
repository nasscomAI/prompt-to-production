skills:
  - name: retrieve_documents
    description: >
      Load all three policy .txt files, parse each into numbered sections and
      clauses indexed by document name and section number for lookup.
    input: >
      A list of file paths to .txt policy documents.
    output: >
      A dict mapping document short name (e.g. "HR Leave Policy") to a list of
      sections, each containing section title and clauses with id + text.
    error_handling: >
      If a file does not exist or cannot be read, print a warning and skip it.
      If no files can be read, return an empty dict.

  - name: answer_question
    description: >
      Take a user question and the indexed document structure, search for the
      answer in a single document, return the answer with citation or the
      refusal template if not found.
    input: >
      question (str), indexed_docs (dict).
    output: >
      A string answer with source document name and section number, or the
      exact refusal template if the question cannot be answered from the
      available documents.
    error_handling: >
      Never blend answers from multiple documents. If multiple documents match,
      return the most specific single-document answer or refuse. Never guess.
