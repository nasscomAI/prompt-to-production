skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files and indexes every clause by document name, section number, and title.
    input: Optional base directory path containing policy text files (str).
    output: Nested dictionary mapping document filenames and section identifiers to section text and metadata (dict).
    error_handling: Raises FileNotFoundError with a clear message if any of the three required policy documents is missing, inaccessible, or corrupt.

  - name: answer_question
    description: Answers staff policy questions strictly from a single document with exact section citations or returns the verbatim refusal template.
    input: User question (str) and indexed policy document dictionary (dict).
    output: String response containing the single-source factual answer with section citations, or the exact refusal template.
    error_handling: Enforces zero cross-document blending by discarding multi-doc merges, rejects hedged hallucinations by refusing rather than guessing, and maintains all prerequisite clauses to prevent condition dropping.
