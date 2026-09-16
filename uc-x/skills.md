skills:
  - name: retrieve_documents
    description: >
      Load all three policy files and index their content by document name and
      section number for source-constrained retrieval.
    input: >
      No user question is required. Read these files from the configured policy
      documents directory: policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: >
      An index containing each document's text, document filename, and section
      boundaries/numbers. Keep documents separate; never merge their claims.
    error_handling: >
      If any required file cannot be loaded or parsed into sections, report the
      specific filename and stop rather than answering from memory or guessing.

  - name: answer_question
    description: >
      Search the indexed policy documents and return a factual answer supported
      by one source document and section, or the exact refusal template.
    input: >
      A natural-language user question and the index produced by
      retrieve_documents.
    output: >
      If one document directly covers the question, return a concise answer
      citing that document filename and section number for every factual claim.
      If the question is not covered, or answering it would require combining
      claims from multiple documents or resolving ambiguity, return exactly:
      "This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
    error_handling: >
      Never guess, use outside knowledge, blend HR/IT/Finance claims, or use
      hedging phrases such as "while not explicitly covered", "typically",
      "generally understood", or "it is common practice". Invalid, unsupported,
      or ambiguous questions must use the refusal template exactly.
