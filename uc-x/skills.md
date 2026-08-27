# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes their content by document name and section number for searchable retrieval.
    input: Directory path containing the 3 policy .txt files (string).
    output: A dictionary mapping document names to their structured sections, each section containing the clause number and full text.
    error_handling: If any policy file is missing or unreadable, report which file failed and continue loading the remaining files.

  - name: answer_question
    description: Searches indexed documents for relevant sections, returns a single-source answer with citation or the refusal template if not covered.
    input: User question (string) and the indexed document store from retrieve_documents.
    output: Either a factual answer citing one document name and section number, or the exact refusal template if the question is not covered in any document.
    error_handling: If the question touches multiple documents, answer from the most directly relevant one only. If a single-source answer cannot be constructed without blending, use the refusal template. Never hedge or speculate.
