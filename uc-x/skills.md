# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: Load all three policy files and index them by document name and section number.
    input: >
      The three filesystem paths to
      policy_hr_leave.txt, policy_it_acceptable_use.txt,
      policy_finance_reimbursement.txt.
    output: >
      A dict keyed by document filename, whose value is a list of
      {section: "X.Y", text: "..."} entries in order. Section numbers
      are detected from the "X.Y" patterns that start a line in each
      file.
    error_handling: >
      Refuse (non-zero exit) if any of the three files is missing,
      unreadable, or contains no parseable section numbers. The
      index must be built fully before answer_question is called.

  - name: answer_question
    description: Answer a user question by quoting a single source document and section, or by emitting the refusal template.
    input: >
      The index returned by retrieve_documents and the user's question
      (a string).
    output: >
      A plain-text answer. Either: (a) a short paragraph with each
      factual claim followed by a [policy_xxx.txt §X.Y] citation, all
      drawn from exactly one document, OR (b) the exact refusal
      template from agents.md, with no variation.
    error_handling: >
      If the question's keywords do not match any single document's
      section text with high confidence, emit the refusal template —
      do not guess. If the question matches sections in two different
      documents, the agent must pick exactly one document (the one
      whose primary topic matches the question's primary noun) and
      answer only from that document, OR emit the refusal template.
      Before returning, scan the candidate answer for any of the
      forbidden phrases listed in agents.md; if any is found, replace
      the answer with the refusal template.
