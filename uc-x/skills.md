skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes them by document name and section number,
      so that every later claim has an address it can be cited from.
    input: >
      paths (list of str) — the three policy .txt files. No other file may be indexed.
    output: >
      dict with keys: docs (mapping of document filename to {reference, sections}) and
      clauses (list of {doc, ref, heading, text, terms}), where terms is the set of
      content words in the clause and ref is the N.M section number. Also returns
      doc_frequency, the number of clauses each term appears in, used to distinguish a
      distinctive term from a stopword.
    error_handling: >
      A missing file exits naming the path — answering from two of three documents would
      silently change which questions are "not covered", which is worse than not running.
      A file with zero parseable clauses exits. Clause text is joined across continuation
      lines and never truncated, because a truncated clause is a dropped condition.

  - name: answer_question
    description: >
      Scores indexed clauses against a question, selects a single governing document, and
      returns either a quoted answer with citations or the refusal template.
    input: >
      question (str), index (dict from retrieve_documents).
    output: >
      dict with keys: outcome ("answer" or "refusal"), document (single filename or None),
      citations (list of {doc, ref}), text (the answer, built only from verbatim clause
      quotations with citations, or the refusal template character for character), and
      reason (why it refused, for the audit trail — printed separately from the answer so
      it can never be mistaken for part of it).
    error_handling: >
      Refuses when: the best match rests only on common terms (no distinctive term);
      the total match score is below the coverage threshold; or two documents score close
      enough that neither is clearly governing. Asserts that the citation set spans
      exactly one document and that no banned hedging phrase is present, and downgrades
      to the refusal template if either assertion fails — so a defective answer is never
      shown rather than being shown with a warning.
