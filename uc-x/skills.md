# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes their content by document name and section number.
    input:
      type: null
      format: None
    output:
      type: dict
      format: A dictionary structure mapping document name and section identifier to section text.
    error_handling: Raises a FileNotFoundError if any of the three required policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to return a single-source answer with a citation or the exact refusal template.
    input:
      type: string
      format: A plain text query representing a policy question.
    output:
      type: string
      format: A plain text response containing either a single-source answer with a document name and section number citation, or the exact refusal template.
    error_handling: Returns the exact refusal template verbatim without any hedging phrases if the input is ambiguous, not covered by the documents, or would require cross-document blending.
