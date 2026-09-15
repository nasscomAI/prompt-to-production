# skills.md — UC-X Ask My Documents

skills:
  - name: retrieve_documents
    description: >
      Loads all three policy files and indexes them by document name and clause
      number, so every later step works on identified clauses rather than free text.
    input: >
      doc_dir (str) — directory holding policy_hr_leave.txt,
      policy_it_acceptable_use.txt and policy_finance_reimbursement.txt.
      Read as UTF-8; CRLF endings and box-drawing separator lines are tolerated.
    output: >
      dict with keys:
        clauses   — list of {document, id, text, section_title, index_terms}, in
                    source order; text is verbatim with line-wrap whitespace collapsed
        idf       — inverse document frequency per term across all clauses, used to
                    weight rare terms above common ones at retrieval time
        documents — the file names successfully loaded
        total     — clause count across the corpus
      Section titles are folded into index_terms but never into text. That is how
      "Who approves leave without pay?" reaches clause 5.2, whose own words are
      only "LWP requires approval from...".
    error_handling: >
      A file missing or unreadable → message to stderr and exit 1; the agent does
      not answer from two documents when it was asked to index three, because a
      silently smaller corpus produces confident refusals for covered questions.
      Zero clauses parsed → exit 1 with the reason.
      A continuation line before any clause id is attached to the clause above it,
      never dropped.

  - name: score_clauses
    description: >
      Ranks every clause in the corpus against a question by IDF-weighted overlap of
      normalised terms.
    input: >
      index (dict) from retrieve_documents; question (str).
    output: >
      list of (clause, score, terms_matched) sorted by score descending, then by
      document name and clause id so equal scores resolve identically every run.
    error_handling: >
      A question of only stopwords yields an empty query and an empty result, which
      the caller turns into the not-covered refusal rather than a default answer.
      Stemming folds plurals before derivational suffixes and then a trailing 'e',
      so 'device' and 'devices' converge — they did not in the first version, and
      the mismatch sent a device question to the wrong document.
      The synonym map is retrieval-only and declared as a constant in app.py: it
      changes which clause is found and never adds a word to what is displayed.

  - name: answer_question
    description: >
      Returns a single-source answer with citations, or one of two fixed refusals.
      This is the skill that enforces "never combine two documents".
    input: "index (dict) and question (str)."
    output: >
      dict with keys status, text, citations, document.
      status is ANSWERED, REFUSED_NOT_COVERED, or REFUSED_CROSS_DOCUMENT.
      On ANSWERED, every citation names the same file and text holds up to four
      clauses from that file, verbatim, ordered by clause number.
      On either refusal, citations is empty and text is the fixed template.
    error_handling: >
      Below the relevance floor — fewer than two distinct content terms matched, or
      a weighted score under the minimum → the not-covered refusal, verbatim, with
      no partial answer attached.
      Runner-up document scoring at least 80% of the winner → the cross-document
      refusal naming both files; neither is used, and nothing is merged.
      Above the floor with one clear winner → clauses from that winner only;
      lower-ranked clauses from other documents are discarded rather than appended.
      No branch of this function can return citations from more than one document.

  - name: check_no_hedging
    description: >
      Scans the rendered response for banned hedging phrases before it is printed —
      the testable form of "never hedge".
    input: "text (str) — the fully rendered response, not the raw clause list."
    output: >
      list of str — every banned phrase found. Empty means the response is clean.
      A non-empty result aborts the run with a non-zero exit rather than printing.
    error_handling: >
      The check runs on the rendered output, so it also covers the refusal templates
      and the framing lines, not only the clause text. Matching is case-insensitive
      substring matching against a fixed declared list; adding or removing a phrase
      is a visible code change a reviewer can object to.
      Because answer text is always clause text reproduced verbatim, this check is
      expected to pass on every run — it exists to prove that, not to repair prose.