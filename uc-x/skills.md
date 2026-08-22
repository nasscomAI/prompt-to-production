# skills.md

skills:
  - name: retrieve_documents
    description: Loads all three CMC policy files and indexes their content by document name and section number.
    input: >
      No parameters (fixed corpus). Reads ../data/policy-documents/
      policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt as plain text.
    output: >
      An index: dict mapping document name -> ordered list of sections,
      where each section holds its number, heading, and full text
      (conditions, limits, dates preserved verbatim).
    error_handling: >
      If a file is missing or unreadable, report the specific filename and
      stop — never answer from a partially loaded corpus.

  - name: answer_question
    description: Searches the indexed documents for the question's answer and returns either a single-source cited answer or the refusal template.
    input: A user question, plain-text string (e.g. "Can I carry forward unused annual leave?").
    output: >
      One of exactly two outputs:
      1. Answer text drawn from ONE document, ending with a citation
         "[document_name], section [N]", with every stated condition intact.
      2. The refusal template verbatim: "This question is not covered in the
         available policy documents (policy_hr_leave.txt,
         policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
         Please contact [relevant team] for guidance." where [relevant team]
         is HR team / IT Helpdesk / Finance team matched to the closest document.
    error_handling: >
      If the answer is absent from all documents, ambiguous, or would require
      combining two documents to state a permission, return the refusal
      template exactly — no hedging, no partial answers, no blended claims.
