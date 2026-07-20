skills:
  - name: retrieve_documents
    description: >
      Loads the three approved policy files and indexes each complete numbered
      clause under its source document name and section reference.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A searchable index of normalized clause text keyed by document filename
      and section number, retaining document boundaries and source order.
    error_handling: >
      Report a missing, unreadable, empty, or malformed policy file clearly.
      Do not substitute another document, merge document content, fabricate a
      section, or index unnumbered text as a numbered policy claim.

  - name: answer_question
    description: >
      Finds a directly supported answer in one indexed policy document and
      returns that answer with its section citation, or returns the exact
      refusal template.
    input: >
      A natural-language question and the document-and-section index produced
      by retrieve_documents.
    output: >
      Either a concise answer based wholly on one source document with that
      document's filename and section number cited for every factual claim, or
      exactly: This question is not covered in the available policy documents
      (policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt). Please contact [relevant team] for
      guidance.
    error_handling: >
      Refuse when no single clause directly supports the requested claim, when
      answers would need to blend documents, or when a material condition is
      ambiguous. Never infer permission, add external practice, omit a source
      limitation, or use hedged hallucination language.
