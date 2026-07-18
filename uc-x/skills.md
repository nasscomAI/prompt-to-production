skills:
  - name: retrieve_documents
    description: Load all three policy text files and index them by document name and section number.
    input: None.
    output: A dictionary mapping document names to their parsed sections and clauses.
    error_handling: Report if any of the three policy files are missing or unreadable.

  - name: answer_question
    description: Search the indexed documents, match key phrases in the user's question, and return a single-source answer with citations or the refusal template.
    input: User question (string) and the indexed documents (dict).
    output: Precise answer with citation or refusal template (string).
    error_handling: Returns the refusal template if the query is out-of-scope, ambiguous, or lacks evidence in the source documents.
