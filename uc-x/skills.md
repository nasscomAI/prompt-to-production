# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files, parses each into structured sections indexed by document name and section number, ready for keyword search.
    input: A list of file paths to policy .txt documents.
    output: A dict keyed by document filename, where each value is a list of clause dicts with keys — section_heading, clause_number, clause_text. Prints confirmation of loaded documents and total clause counts.
    error_handling: If any file is not found, prints a warning and continues loading the remaining files. If no files can be loaded, prints an error and exits.

  - name: answer_question
    description: Searches indexed documents for clauses relevant to the user's question, returns a single-source answer with citation, or the exact refusal template if not found.
    input: The user's question string and the indexed document data from retrieve_documents.
    output: A formatted answer string containing the answer text and citation [Source: filename, Section X.X], or the exact refusal template.
    error_handling: If relevant clauses are found in multiple documents, answers from the single most relevant document only and notes the other may also be relevant. Never blends. If no relevant clauses are found, returns the exact refusal template verbatim. Never hedges.
