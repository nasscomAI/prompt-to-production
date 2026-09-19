# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Loads the three policy files and indexes every numbered clause by document name and section number.
    input: >
      doc_dir (string, default ../data/policy-documents) containing policy_hr_leave.txt,
      policy_it_acceptable_use.txt and policy_finance_reimbursement.txt.
    output: >
      (clauses, idf) — clauses is a list of {doc, section, heading, text, tokens} with
      wrapped lines joined; idf maps each normalised word to its rarity across all clauses.
    error_handling: >
      Any of the three files missing → refuses to start (answers would silently miss a
      document). Divider lines and document headers are not indexed as clauses.

  - name: answer_question
    description: Finds the clauses that best match a question and returns a single-document cited answer or the exact refusal template.
    input: >
      question (string), plus clauses and idf from retrieve_documents.
    output: >
      string — either "Source: <doc> — section <ids>" followed by up to 3 verbatim clauses
      from that one document, or the refusal template from agents.md, unchanged.
    error_handling: >
      Empty question, no match, or best clause backed by fewer than 2 meaningful question
      terms → refusal template. A different document scoring within 90% of the best →
      refusal template (no blending). A clause word is credited to only one question term
      and synonym matches count half, so a shared word like 'device' cannot inflate a
      wrong document. Any hedging phrase in a built answer is a hard error.
