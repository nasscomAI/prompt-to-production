# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy files and indexes them by document name and section number so answers can be cited.
    input: Paths to the three policy files under ../data/policy-documents/.
    output: An index mapping each document name to its numbered clauses with verbatim text.
    error_handling: Raises a clear error if a policy file is missing or unreadable; skips decorative lines (headers, separators) rather than indexing them.

  - name: answer_question
    description: Searches the indexed documents, returns a single-source answer with citation, or the exact refusal template when the question is not covered.
    input: A question string plus the index from retrieve_documents.
    output: Either an answer drawn from exactly one document and one section with a source citation, or the refusal template verbatim.
    error_handling: Refuses (exact refusal template) when the question matches no clause, matches clauses from different documents, or is ambiguous; never blends documents and never invents content.
