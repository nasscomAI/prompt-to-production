# skills.md

skills:
  - name: retrieve_documents
    description: Loads and indexes all policy files by document name and section number.
    input: List of policy file paths.
    output: A nested dictionary structure where keys are document names and sub-keys are section numbers.
    error_handling: Skips files that cannot be read and notifies the user.

  - name: answer_question
    description: Searches the indexed documents for a query and returns a single-source answer with citations or a refusal.
    input: User question string and indexed documents.
    output: A string response (factual answer + citation) or the standard refusal template.
    error_handling: Refuses if information appears in multiple documents or is missing entirely.
