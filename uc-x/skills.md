# skills.md

skills:
  - name: retrieve_documents
    description: Loads all 3 policy .txt files and indexes their content by document name, section, and clause number, so every fact can be traced back to its exact source.
    input: >
      A list of file paths to the 3 policy documents (policy_hr_leave.txt,
      policy_it_acceptable_use.txt, policy_finance_reimbursement.txt).
    output: >
      A list of clause dicts, each with keys: doc (source filename), section
      (the enclosing section header), clause (clause number, e.g. "3.1"),
      text (the clause's full text, line-wrapping collapsed).
    error_handling: >
      If a file cannot be read or contains no numbered clauses, raise an
      error — a missing source document must never be silently skipped,
      since that would make the "not covered" refusal unreliable.

  - name: answer_question
    description: Scores every indexed clause against the question, picks the single best-matching document, and returns either a citation-backed answer built only from that document's clauses, or the exact refusal template.
    input: >
      The clause index from retrieve_documents, and a question (str).
    output: >
      A dict with keys: answer (str — either the cited answer text or the
      refusal template verbatim) and citations (list of "doc, Clause X.Y"
      strings used, empty on refusal).
    error_handling: >
      If no clause scores any relevant overlap with the question, or if two
      different documents are close enough in relevance that picking one
      over the other would be a guess, return the refusal template exactly
      as written in README.md — never blend clauses from two documents into
      one answer, and never hedge with phrases like "typically" or "while
      not explicitly covered".
