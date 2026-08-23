skills:
  - name: retrieve_documents
    description: Load and search policy documents by document and section.
    input: User question
    output: Matching policy section
    error_handling: Return no match if nothing relevant exists.

  - name: answer_question
    description: Answer using only one matching document.
    input: Retrieved section
    output: Answer with document and section citation.
    error_handling: Return refusal template if answer is unavailable.