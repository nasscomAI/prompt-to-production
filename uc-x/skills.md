# skills.md

skills:
  - name: retrieve_documents
    role: >
      Load and index the approved policy documents for the Ask My Documents
      system. This skill retrieves source material only; it does not interpret
      policy or answer employee questions.
    intent: >
      Return a complete, traceable index of policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt, with
      every passage associated with its document name and section number.
    context: >
      May use only the three policy files in ../data/policy-documents/. It must
      not use general company knowledge, external sources, inferred policy, or
      content from unapproved files.
    enforcement:
      - "Load only policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt."
      - "Preserve each passage's source document name and section number in the index."
      - "Do not merge, summarize, or infer relationships between passages from different documents."
      - "If an approved document is unavailable, return a retrieval error identifying that document; do not substitute another source."
    input: >
      A retrieval request for the approved policy corpus; optionally, a document
      name or search query as a string.
    output: >
      A structured list of matching passages, each containing the passage text,
      document name, and section number; or a retrieval error.
    error_handling: >
      Reject unapproved document names and report missing or unreadable approved
      files without fabricating content.

  - name: answer_question
    role: >
      Answer employee policy questions using the indexed policy corpus. This
      skill is limited to a single supported source document for each answer.
    intent: >
      Return either a precise answer supported by one policy document and a
      document-name-plus-section citation for every factual claim, or the exact
      refusal template when the documents do not cover the question.
    context: >
      May use only passages returned by retrieve_documents from
      policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt. It must not use external knowledge,
      assumptions, common practice, or blended claims across documents.
    enforcement:
      - "Never combine claims from two different documents into a single answer."
      - "Cite the source document name and section number for every factual claim."
      - "Never use the phrases: while not explicitly covered, typically, generally understood, or it is common practice."
      - >
        If the question is not covered, is ambiguous across documents, or cannot
        be answered from one document, return exactly: This question is not
        covered in the available policy documents
        (policy_hr_leave.txt, policy_it_acceptable_use.txt,
        policy_finance_reimbursement.txt). Please contact [relevant team] for
        guidance.
    input: A single employee policy question as plain text.
    output: >
      A single-source policy answer with inline document-name-and-section
      citation(s), or the exact refusal template.
    error_handling: >
      Treat invalid, unsupported, cross-document, and insufficiently specific
      questions as not covered and return the exact refusal template.
