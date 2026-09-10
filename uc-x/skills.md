# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all three policy text files and indexes their content by document name and section number for efficient lookup.
    input: Directory path containing the three policy .txt files.
    output: A nested dict indexed as {document_name: {section_number: section_content}} covering all sections across all three documents.
    error_handling: If any of the three expected files is missing, reports which file could not be loaded and continues with the remaining files. Never silently skips a missing file.

  - name: answer_question
    description: Searches the indexed documents for sections relevant to the question, returns a single-source answer with citation, or the exact refusal template if the question is not covered.
    input: A user question (string) and the document index from retrieve_documents.
    output: Either an answer string citing one document name and section number, or the exact refusal template string.
    error_handling: If the question matches sections from multiple documents, answers from the single best-matching document only — never blends. If no section matches, returns the refusal template verbatim. If a matched section contains a multi-condition obligation, all conditions are included in the answer.
