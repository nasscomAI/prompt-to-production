# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes them by document name and section
      number, one entry per numbered clause, with IDF weights computed across the
      whole corpus.
    input: >
      doc_dir (str) — directory holding the three .txt policies.
    output: >
      dict with keys:
        clauses — list of {document, section, section_title, id, text, terms, bigrams}
        idf     — dict term -> inverse document frequency across clauses
        total   — clause count
      The document name travels with every clause. It is never dropped, because
      the single-source rule downstream depends on knowing where each clause
      came from.
    error_handling: >
      A missing policy file raises CorpusError and the run exits 2 — it does not
      proceed with two of the three documents, because an answer assembled from a
      partial corpus would silently be missing the clause that governs it. A
      zero-clause index also raises rather than returning empty, since an empty
      index makes every question refusable for the wrong reason.

  - name: answer_question
    description: >
      Scores every clause against the question, then returns either a
      single-source cited answer or the refusal template.
    input: >
      corpus (dict) from retrieve_documents, question (str).
    output: >
      tuple (answer_text: str, sources: list[(document, clause_id)]).
      sources is empty exactly when the answer is the refusal template, and
      otherwise contains entries from one document only.
    error_handling: >
      Below the coverage floor — fewer than 2 distinct matched content terms, or
      a score under the threshold — it returns the refusal template rather than
      the best available guess. A tie across documents is resolved by taking the
      single highest-scoring clause and its section; it is never resolved by
      including both. There is no code path that appends a clause from a second
      document, so blending cannot occur through a bug either.

  - name: hedging_in
    description: >
      Reports which banned hedging phrases appear in a candidate answer. Runs
      over the assistant's own output and can be run over any other system's.
    input: >
      text (str).
    output: >
      list[str] — the banned phrases found, empty when clean.
    error_handling: >
      Reports rather than raises. It is a detector, so it must be able to run
      against output it did not produce.

  - name: run_test_suite
    description: >
      Runs the 7 README questions and scores each against the behaviour it must
      produce — expected document and section, or the exact refusal template.
    input: >
      corpus (dict).
    output: >
      Printed per-question report plus a pass count; process exit code 0 only if
      all 7 pass.
    error_handling: >
      Checks three failure classes independently: more than one distinct source
      document (BLENDED), a banned phrase anywhere in the answer (HEDGING), and
      wrong or altered refusal text. The personal-phone question is allowed to
      pass either by citing IT section 3 or by refusing, matching the README,
      which accepts both; every other question has exactly one correct outcome.
