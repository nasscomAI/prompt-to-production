skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes them by document name and numbered section.
    input: Paths to the policy text files.
    output: Structured document content keyed by document name, section title, and clause number.
    error_handling: Reject missing or unreadable files and never fabricate sections that are not present.

  - name: answer_question
    description: Searches the indexed documents and returns a single-source cited answer or the fixed refusal template.
    input: A user question and the indexed policy documents.
    output: A plain-text answer with document and section citations, or the exact refusal template.
    error_handling: Refuse if the answer is not covered, ambiguous, or would require combining claims from multiple documents.
