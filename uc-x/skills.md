# skills.md

skills:
  - name: retrieve_documents
    description: >
      Loads all 3 policy files and indexes them by document name and section
      number, enabling lookup by topic or keyword.
    input: >
      Void — no input needed. Reads from the fixed paths:
      ../data/policy-documents/policy_hr_leave.txt,
      ../data/policy-documents/policy_it_acceptable_use.txt,
      ../data/policy-documents/policy_finance_reimbursement.txt
    output: >
      A structured index mapping document name → section number → section
      content, ready for retrieval by the answer_question skill.
    error_handling: >
      If a file is missing or unreadable, return an error listing which files
      could not be loaded and continue with available documents.

  - name: answer_question
    description: >
      Searches the indexed policy documents for a single-source answer to the
      user's question and returns the answer with citation or the refusal
      template.
    input: >
      A natural-language question string about company policy.
    output: >
      Either a single-source answer with document name and section citation,
      or the exact refusal template: "This question is not covered in the
      available policy documents (policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
      Please contact [relevant team] for guidance."
    error_handling: >
      If the question touches multiple documents or is ambiguous across sources,
      return the refusal template rather than blending information.
