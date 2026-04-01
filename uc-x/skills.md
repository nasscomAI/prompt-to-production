skills:

* name: retrieve_documents
  description: Loads all policy documents and stores them with document names.
  input: Folder containing policy text files.
  output: Dictionary mapping document name to its content lines.
  error_handling: If a document cannot be loaded, return an error and stop execution.

* name: answer_question
  description: Searches the documents for a clause matching the user question.
  input: Document dictionary and question string.
  output: Exact clause with document name citation or refusal template.
  error_handling: If no clause matches the question, return the refusal template.
