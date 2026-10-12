skills:
  - name: retrieve_documents
    description: Loads the three CMC policy files and indexes every numbered clause by document name and section number.
    input: >
      docs_dir (str) — directory containing policy_hr_leave.txt,
      policy_it_acceptable_use.txt and policy_finance_reimbursement.txt (UTF-8 text,
      clauses numbered N.N, wrapped over several lines).
    output: >
      list of clause records {document: str (file name), section: str like "3.1",
      heading: str (section heading), text: str (full clause, line wraps joined),
      terms: set of normalised search terms}, plus document-frequency statistics used
      for ranking.
    error_handling: >
      Any of the three files missing or containing no numbered clauses -> stop with an
      error naming the file; the assistant never runs on a partial document set
      (otherwise a question would be refused or answered from the wrong document).
      Wrapped clause lines are joined so no condition is cut off.

  - name: answer_question
    description: Searches the indexed clauses and returns either a single-document answer with section citations or the exact refusal template.
    input: >
      question (str, free text from the user) and the index returned by
      retrieve_documents.
    output: >
      str — either "Source: <document> \n [section N.N] <full clause text> ..." with
      1–3 clauses all from the same document, or the refusal template verbatim.
    error_handling: >
      Empty question -> ask the user to type a question. Best clause covers fewer than
      half of the question's key terms -> refusal template (prevents hedged
      hallucination). A clause from a second document that matches as many of the question's
      key terms and scores within 15% of the best -> refusal template (prevents
      cross-document blending). Generic verbs (take, apply, need) are not counted as
      key terms, so they cannot push a covered question into a refusal. Answer text
      is checked for hedging phrases before it is returned; if any appear the refusal
      template is returned instead. Clauses are quoted in full so no condition is
      dropped. Permission questions ("Can I…") that match only a prohibition also get
      the same section's scope-setting "may … only" clause, so the answer states what is
      permitted as well as what is not (condition dropping).
