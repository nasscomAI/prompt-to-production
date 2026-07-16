skills:
  - name: retrieve_documents
    description: Loads and indexes all three policy text files, parsing them by sections and document name.
    input: File paths of the three policy documents.
    output: A structured database or dict representing sections of each document.
    error_handling: Raises an error if any file is missing or fails to load.

  - name: answer_question
    description: Evaluates a user query against the indexed documents, and generates either a precise single-source answer with citations or the exact refusal template.
    input: User query string and indexed document collection.
    output: The response string.
    error_handling: Strict refusal template matches for out-of-scope or cross-document blended queries.
