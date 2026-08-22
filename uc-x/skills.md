skills:
  - name: retrieve_documents
    description: Loads all 3 policy text files and indexes them by document name and section number.
    input: None.
    output: A dictionary of indexed documents with sections.
    error_handling: Fail gracefully if any of the files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to find a single-source answer with proper citation, or outputs the refusal template.
    input: Question query string (str), indexed documents (dict).
    output: Answer text string (str) with citation or refusal.
    error_handling: Output the exact refusal template if there is any cross-document blending risk or if no direct match is found.
