skills:
  - name: retrieve_documents
    description: Load all policy files and index them by document name and section number for cited retrieval.
    input: "List of policy file paths."
    output: "Indexed structure: {doc_name: {section_number: section_text}}."
    error_handling: "If any file is missing or unreadable, return an explicit missing-document error and do not synthesize answers."

  - name: answer_question
    description: Answer a policy question using one document source with citation, or return the exact refusal template.
    input: "User question string and indexed policy corpus."
    output: "Either {answer, source_document, section_number} or the exact refusal template text."
    error_handling: "If evidence spans multiple documents or is ambiguous, refuse rather than blend; if no evidence is found, return the exact refusal template."
