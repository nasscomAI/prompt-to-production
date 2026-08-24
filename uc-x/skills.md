# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads the three policy files and indexes them by document name and section
      number so every factual claim can be traced to a single source.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt, and
      policy_finance_reimbursement.txt.
    output: >
      A per-document map of section number to verbatim clause text.
    error_handling: >
      Raises an error if a policy file is missing. Every clause keeps its exact
      wording — nothing is paraphrased at load time.

  - name: answer_question
    description: >
      Answers a question using exactly one source document, quoting the relevant
      section and citing its name and number, or refuses with the exact template.
    input: >
      A question string from the user.
    output: >
      Either a single-source cited answer (document name + section number + verbatim
      clause text) or the exact refusal template.
    error_handling: >
      Never blends claims from two different documents into one answer — the
      personal-phone question is answered from IT policy section 3.1 only or refused.
      Never uses hedging phrases. If the question is not covered by any document,
      the refusal template is returned verbatim.
