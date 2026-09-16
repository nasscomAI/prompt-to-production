# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy .txt files and indexes every numbered clause by
      document name and section number, preserving verbatim text.
    input: >
      paths (list[str]) — the three files in data/policy-documents/
    output: >
      dict:
        clauses   — list of {doc, doc_title, section_number, section_title,
                    clause_id, text, tokens}
        by_doc    — {filename: [clause, ...]} preserving file order
        idf       — {token: inverse document frequency} computed across clauses,
                    so common policy words ("employees", "must") carry less weight
                    than distinguishing ones ("encashment", "gambling")
      Clause text is stored verbatim (hard wraps joined, whitespace collapsed) so
      any answer built from it remains a substring of the source file.
    error_handling: >
      - any file missing/unreadable -> raises naming the file; the CLI exits
        rather than answering from a partial corpus, because an index silently
        missing one policy produces confident answers about the wrong document.
      - a file that parses to zero clauses -> raises; wrong file shape is never
        treated as an empty-but-valid document.
      - duplicate clause ids within a document -> kept and reported, never merged.

  - name: answer_question
    description: >
      Answers a question from exactly ONE document, or refuses with the fixed
      template. Selects the source document before assembling any text.
    input: >
      index (dict) — output of retrieve_documents
      question (str)
    output: >
      dict:
        status    — ANSWERED | REFUSED_NOT_COVERED | REFUSED_AMBIGUOUS
        doc       — source filename (ANSWERED only)
        sections  — list of clause ids quoted (ANSWERED only)
        body      — verbatim clause text (ANSWERED), or the refusal template
                    reproduced exactly (either REFUSED status)
        citation  — "policy_it_acceptable_use.txt — section 3.1" (ANSWERED only)
        scores    — per-document relevance, for auditability of the decision
      Answer text is EXTRACTIVE: every sentence is a verbatim substring of the
      cited document, which is what makes hedging and condition-dropping
      impossible rather than merely discouraged.
    error_handling: >
      - best score below the relevance floor -> REFUSED_NOT_COVERED with the
        template. A weak match is never returned dressed in a citation.
      - runner-up document within 80% of the winner -> REFUSED_AMBIGUOUS with the
        template. This is the cross-document blending guard, and it fires on the
        personal-phone question by design.
      - empty or whitespace-only question -> re-prompts in the CLI; never treated
        as a request to summarise everything.
      - a question whose terms match clauses in several documents equally -> the
        ambiguity rule applies before any text is assembled, so a blended answer
        cannot be constructed even transiently.

  - name: verify_answer
    description: >
      Self-check run over the README's 7 test questions, asserting the enforcement
      rules hold on real output rather than in principle.
    input: >
      index (dict)
    output: >
      list of per-question results with pass/fail on:
        single_source  — at most one document cited
        extractive     — every answer line is a substring of the cited document
        no_hedging     — no banned hedging phrase appears
        citation       — every ANSWERED response names document and section
        refusal_exact  — every refusal matches the template character-for-character
        expectation    — matches the behaviour the README specifies per question
      Prints a table and exits non-zero on any failure.
    error_handling: >
      Never reports a pass it did not verify. A question whose expected behaviour
      is "single-source OR refusal" is checked against both acceptable outcomes
      and reports which one occurred, rather than silently accepting anything.
