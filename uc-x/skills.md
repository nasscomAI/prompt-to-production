skills:
  - name: retrieve_documents
    description: Load all three policy files and index every numbered clause by document name and section number.
    input: >
      Optional directory path. Default is the repo data/policy-documents
      folder containing policy_hr_leave.txt, policy_it_acceptable_use.txt,
      and policy_finance_reimbursement.txt.
    output: >
      A dict keyed by filename. Each value has clauses: a list of
      {id, text, heading} where id is like "3.1".
    error_handling: >
      Missing file → raise FileNotFoundError naming the file. Empty files
      index as zero clauses. Decorative separator lines are ignored.

  - name: answer_question
    description: Search the index and return a single-source cited answer or the exact refusal template.
    input: >
      documents dict from retrieve_documents, and question (str).
    output: >
      A string. Either cited sentences from exactly one filename, or the
      refusal template with no extra preamble or hedge.
    error_handling: >
      No matching document, culture/opinion questions, or two documents
      tying for relevance → refusal template exactly. Never guess a
      permission. Never quote a second file in the same answer.
