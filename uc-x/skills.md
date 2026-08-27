skills:
  - name: retrieve_documents
    description: Loads the three policy text files and indexes their clauses by document name and section/clause number.
    input: None. Loads from hardcoded relative or absolute paths.
    output: A dictionary/object mapping document names and clause IDs to their exact text contents.
    error_handling: If any of the three policy files are missing or unreadable, raises a FileNotFoundError or ValueError.

  - name: answer_question
    description: Searches the indexed document clauses to answer an employee's question, returning a single-source cited answer or the exact refusal template.
    input: A string representing the user's question, and a dictionary of indexed documents.
    output: A string containing the cited answer or the refusal template.
    error_handling: If the question cannot be answered using a single source clause, returns the refusal template verbatim.
