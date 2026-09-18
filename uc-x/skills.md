# skills.md

skills:
  - name: retrieve_documents
    description: >
      Load all three supplied CMC policy documents and index their numbered
      sections by document name and section number for grounded retrieval.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A structured collection of policy sections containing document name,
      section number, and source text.
    error_handling: >
      If a document is missing, unreadable, or cannot be parsed into numbered
      sections, report the problem and do not invent or reconstruct missing
      policy content.

  - name: answer_question
    description: >
      Search the indexed policy sections for the user's question and return a
      supported answer from one source document with document name and section
      citation, or return the exact refusal template when the question is not
      sufficiently covered.
    input: >
      A user question and the indexed sections from the three policy documents.
    output: >
      A grounded answer containing only claims supported by one policy
      document, with a source document name and section number for every
      factual claim, or the exact required refusal template.
    error_handling: >
      Never blend claims from different documents, never invent missing
      information, never use hedged unsupported language, and refuse using the
      exact template when the question is not sufficiently covered by one
      source.