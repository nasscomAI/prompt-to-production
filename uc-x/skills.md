# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes them by document name and section
      number.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt and
      policy_finance_reimbursement.txt.
    output: >
      An index mapping document name → section number → section text, keeping each
      document separate (never merged).
    error_handling: >
      Reports any document that is missing or unreadable; flags sections that could
      not be parsed; keeps documents as distinct sources.

  - name: answer_question
    description: >
      Answers a user question from the indexed documents with a single-source
      answer + citation, or the verbatim refusal template.
    input: >
      A free-text question string and the document index from retrieve_documents.
    output: >
      An answer citing the document name and section number, OR the exact refusal
      template when the question is not covered.
    error_handling: >
      Refuses (exact refusal template) when the question is not in any document;
      refuses when a complete answer would require merging claims from two documents;
      never uses hedging phrases such as "while not explicitly covered".