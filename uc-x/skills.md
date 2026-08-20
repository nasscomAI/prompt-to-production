skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name.
    input: List of file paths (Array of Strings).
    output: Dictionary mapping document names to their text content.
    error_handling: Return error if a file is missing.

  - name: answer_question
    description: Searches indexed documents and returns a single-source answer with citation OR exactly the refusal template.
    input: Question string and indexed documents text.
    output: Answer string.
    error_handling: Refuse exactly as per template if ambiguous or not found.
