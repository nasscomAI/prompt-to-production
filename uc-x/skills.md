skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name and section number.
    input: No runtime input beyond the fixed document paths in this UC.
    output: A dictionary of document names mapped to section IDs and section text.
    error_handling: If a document cannot be parsed into numbered sections, fail rather than answering from incomplete data.

  - name: answer_question
    description: Answers a user question from a single document with citations or returns the exact refusal template.
    input: A free-form policy question string plus the indexed documents.
    output: A single-source answer with citations or the refusal template.
    error_handling: If the question is ambiguous, unsupported, or matched by multiple documents at the same strength, return the refusal template.
