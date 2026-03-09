# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name for lookup.
    input: No arguments — paths are hardcoded to the 3 CMC policy documents.
    output: Dict mapping document name (str) to full document content (str).
    error_handling: Prints WARNING if a document file is not found. Continues with available documents.

  - name: answer_question
    description: Searches indexed knowledge base for a single-source answer with citation, or returns refusal template if not found.
    input: question (str) — natural language question from the user.
    output: Answer string with source document and section number, or exact refusal template string.
    error_handling: If no KB entry matches, returns refusal template. Never guesses, infers, or blends across documents.