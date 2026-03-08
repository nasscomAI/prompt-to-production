# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes content by document name and section number.
    input: doc_dir (str) — path to the directory containing policy text files.
    output: A dict keyed by document filename, each value a dict keyed by section number mapping to section text.
    error_handling: >
      If a file is missing or unreadable, logs a warning and continues with
      available documents. If no documents load, prints an error and exits.

  - name: answer_question
    description: Searches indexed documents for the best single-source answer, returns it with citation or uses the refusal template.
    input: question (str), document_index (dict from retrieve_documents).
    output: A string containing the answer with document name + section citation, or the exact refusal template.
    error_handling: >
      If multiple documents contain relevant sections, answers from the most
      specific single source only — never blends. If no section matches,
      returns the refusal template exactly.
