# skills.md — UC-X Policy Q&A Assistant

skills:
  - name: load_policies
    description: >
      Loads the three policy documents and indexes every numbered clause with its
      source document name and clause reference.
    input: >
      Paths to policy_hr_leave.txt, policy_it_acceptable_use.txt and
      policy_finance_reimbursement.txt (strings).
    output: >
      A clause index where each entry maps a question to the best single
      (document, clause_number, clause_text) match.
    error_handling: >
      A missing or unreadable policy file aborts startup with a descriptive
      error; clauses that fail to parse are reported instead of silently dropped.

  - name: answer_question
    description: >
      Answers one policy question from a single best-matching source clause with
      a document + clause citation.
    input: >
      A question string and the clause index from load_policies.
    output: >
      Either an answer with a single citation naming the source document and
      clause, or the fixed refusal template when nothing matches.
    error_handling: >
      When several clauses match, the single highest-scoring clause wins (ties go
      to the earliest clause), and the answer is never blended across documents.
      A question with no clause match receives the verbatim refusal template.