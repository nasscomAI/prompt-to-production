skills:
  - name: retrieve_documents
    description: Loads all policy text files and indexes the content by document name and section number.
    input: Paths to the three policy documents.
    output: Structured index of documents.
    error_handling: Logs warnings if any policy document is missing.

  - name: answer_question
    description: Searches the indexed policies for the answer to a question and returns a cited response or the refusal template.
    input: Question string.
    output: Answer string and citation, or refusal template.
    error_handling: Returns the exact refusal template if no clear single-source answer is found.
