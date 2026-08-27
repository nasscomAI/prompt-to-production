# skills.md

skills:
  - name: retrieve_documents
    description: Loads the HR, IT, and Finance policy files and indexes them by document name and section number.
    input: None
    output: A structured index of policy document contents categorized by name and section.
    error_handling: Throws an error if any of the three policy files are missing or unreadable.

  - name: answer_question
    description: Searches the indexed documents to return a single-source answer with citations or the mandatory refusal template.
    input: String (employee's question)
    output: String (Answer + Citation OR exact refusal template)
    error_handling: Returns the mandatory refusal template if no clear single-source answer is found or if the question is outside the scope.
