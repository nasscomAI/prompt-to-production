skills:
  - name: retrieve_documents
    description: Loads all 3 policy files and indexes them by document name and section number.
    input: List of paths to the 3 policy files (Array/List of Strings).
    output: A structured index of all sections mapped to their source document and section number (JSON/Dictionary).
    error_handling: Raises an error if any of the three required policy documents are missing or unreadable.

  - name: answer_question
    description: Searches indexed documents and returns a strictly single-source answer with a citation, or the exact refusal template.
    input: User question (String) and the structured index of all policy documents (JSON/Dictionary).
    output: A single-source answer including citation, or the exact verbatim refusal template (String).
    error_handling: Refuses to guess or blend rules; immediately returns the refusal template when a clear, single-document answer cannot be found.
