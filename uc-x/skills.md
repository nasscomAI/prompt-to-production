skills:

  - name: retrieve_documents
    description: >
      Loads the three supplied policy documents and indexes their numbered
      sections by document filename and section number.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      Structured collection of policy sections containing filename, section
      number, and source text.
    error_handling: >
      If a policy file cannot be read or numbered sections cannot be extracted,
      report the error and do not invent policy content.

  - name: answer_question
    description: >
      Searches the indexed policy sections and returns a single-source answer
      with filename and section citation, or the exact refusal template.
    input: >
      A natural-language policy question and the indexed policy sections.
    output: >
      A concise answer supported by one policy document with section citation,
      or the exact refusal template when the question is uncovered, ambiguous,
      or would require cross-document blending.
    error_handling: >
      Refuse using the exact required refusal template when no single source
      supports the answer or when answering would require combining claims
      from multiple documents. Never guess or infer missing policy information.