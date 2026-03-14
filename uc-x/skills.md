skills:
  - name: retrieve_documents
    description: Loads the three required policy files and parses them to index sections by document name and section number.
    input: None required (reads from fixed paths).
    output: A structured dictionary of policy sections indexed by document and section number.
    error_handling: System exits if any of the three policy documents cannot be found.

  - name: answer_question
    description: Takes a user's question, searches the indexed documents, and returns a single-source answer with a citation, or explicitly triggers the refusal template.
    input: user_question (string) and document_index (dictionary)
    output: The direct answer string with citation, or the verbatim refusal template.
    error_handling: Triggers refusal template if multiple documents conflict, or if information is absent. Never guesses.
