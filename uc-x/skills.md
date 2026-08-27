# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files, indexing them by document name and section number strictly to prevent cross-bleeding.
    input: List of file paths to policy documents.
    output: Indexed dictionary mapping document names and sections to text.
    error_handling: Returns I/O fault if files are completely unavailable.

  - name: answer_question
    description: Searches indexed documents to return a single-source answer with citation or the refusal template.
    input: User question text and the indexed documents object.
    output: A string containing the exact answer and citation, or the strict refusal template.
    error_handling: If multiple documents contain conflicting or partial answers, immediately aborts synthesis and falls back to the exact refusal template to prevent blending.

