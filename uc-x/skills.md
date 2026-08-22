skills:
  - name: retrieve_documents
    description: >
      Loads all three policy documents and indexes their content by document
      name and numbered section.
    input: >
      Three UTF-8 text policy files: policy_hr_leave.txt,
      policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: >
      Structured document index containing document names, section numbers,
      and section text.
    error_handling: >
      If a required document cannot be loaded, report the missing document
      and do not answer questions using incomplete policy data.

  - name: answer_question
    description: >
      Answers a policy question using a single supported source document and
      provides the document name and section citation.
    input: >
      A user question and the structured policy document index.
    output: >
      A concise answer supported by one document and section citation, or the
      exact refusal template when the question is not covered or is ambiguous.
    error_handling: >
      Refuse rather than guess when the answer is not explicitly supported
      by the documents or would require combining unsupported claims.