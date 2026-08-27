skills:
  - name: retrieve_documents
    description: Loads and indexes all policy documents by section number.
    input: Policy document file paths
    output: Structured indexed document collection
    error_handling: Refuses if documents cannot be loaded

  - name: answer_question
    description: Returns a single-source cited policy answer or refusal.
    input: User question text
    output: Policy answer with citation or refusal template
    error_handling: Refuses ambiguous or unsupported questions