skills:
  - name: retrieve_documents
    description: Loads all three policy text files and indexes their content by document name and section number for efficient searching.
    input: List of file paths to the three policy .txt files (list of strings).
    output: A dictionary indexed by document name, containing sections with numbers and content.
    error_handling: If any file is missing or unreadable, raise an error. Ensure sections are parsed correctly to prevent misindexing that could lead to cross-document blending.

  - name: answer_question
    description: Searches the indexed documents for the question, returns a single-source answer with citation or the exact refusal template.
    input: Question (string) and the indexed documents (dict).
    output: Answer string with citation or refusal template.
    error_handling: If question matches multiple documents, refuse to avoid blending. For hedged hallucination, use refusal template instead of hedging. For condition dropping, ensure full conditions are included. If no match, use exact refusal template.
