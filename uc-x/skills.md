skills:
  - name: retrieve_documents
    description: Load and index all policy documents.
    input: File paths of policy documents.
    output: Dictionary mapping document names to text.
    error_handling: If a file cannot be opened, return NEEDS_REVIEW flag.

  - name: answer_question
    description: Search the documents for information relevant to the question.
    input: User question and indexed documents.
    output: Answer text with citation or refusal message.
    error_handling: If answer is not found, return refusal template.