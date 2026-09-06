skills:
  - name: retrieve_documents
    description: Loads the three approved policy documents and indexes their content by document name and section number.
    input: Three policy text files in TXT format.
    output: An indexed collection of policy content organized by document name and section number.
    error_handling: Reject missing or unreadable policy documents and do not answer from outside sources.

  - name: answer_question
    description: Answers a policy question using only a single relevant document and provides the required source citation.
    input: A user policy question as plain text and the indexed policy documents.
    output: A single-source answer with document name and section number, or the exact refusal template when the question is not covered.
    error_handling: If the question is ambiguous, unsupported, or requires combining claims from different documents, return the exact refusal template instead of guessing or blending policies.