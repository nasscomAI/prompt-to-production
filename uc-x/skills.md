# skills.md

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy documents and indexes their content by document
      name and numbered section so answers can be traced to a single source.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A structured collection of policy sections keyed by document name and
      section number.
    error_handling: >
      If any document cannot be read or its sections cannot be identified,
      report an explicit error and do not invent or infer missing content.

  - name: answer_question
    description: >
      Searches the indexed policy sections and returns a source-grounded
      answer from one document and section, or the exact refusal template.
    input: >
      A user question and the indexed policy documents.
    output: >
      A concise answer containing only claims supported by one source
      document, with the document name and section number cited, or the exact
      required refusal template when the question is not covered or would
      require cross-document blending.
    error_handling: >
      If the question is ambiguous, unsupported, or requires combining claims
      from multiple documents, refuse using the exact required refusal
      template rather than guessing or blending information.
