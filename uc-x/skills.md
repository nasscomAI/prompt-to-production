# skills.md

skills:
  - name: retrieve_documents
    description: Load the policy documents and organize them by document name and section number.
    input: File paths of policy documents.
    output: Structured dictionary containing document name, section numbers, and text.
    error_handling: If a file cannot be read, return an error and stop execution.

  - name: answer_question
    description: Search the policy documents and return a single-source answer with citation.
    input: User question and indexed policy documents.
    output: Answer with document name and section number OR refusal template.
    error_handling: If no matching policy is found, return the refusal template exactly.