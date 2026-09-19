# UC-X skills

skills:
  - name: retrieve_documents
    description: Load the three policy files and index their numbered sections by document and section.
    input: Repository root containing data/policy-documents.
    output: A document-scoped index of section numbers and source text.
    error_handling: Reject missing files; never replace a missing policy with outside knowledge.

  - name: answer_question
    description: Return a single-source cited policy answer or the exact refusal template.
    input: User question and the indexed policy documents.
    output: One answer with filename and section citation, or the exact refusal string.
    error_handling: Refuse unsupported questions and never blend evidence from different files.
