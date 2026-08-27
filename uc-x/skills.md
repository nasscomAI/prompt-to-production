skills:
  - name: retrieve_documents
    description: Loads and parses the HR, IT, and Finance policy text files, indexing them by section number.
    input: File paths to the three policy documents.
    output: A structured index of all policy sections and titles.
    error_handling: System reports an error if any of the core policy files are metadata-incomplete or missing.

  - name: answer_question
    description: Searches the indexed sections for keywords related to the query and formats a compliant response.
    input: User query as a string.
    output: A single-source answer with a citation or the refusal template.
    error_handling: Triggers the refusal template if the highest matching score across all documents is below a confidence threshold.
