# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a policy .txt file and returns it as structured numbered sections and
      clauses, so that every later step operates on identified clauses rather than
      on free text.
    input: >
      path (str) — path to ../data/policy-documents/policy_hr_leave.txt.
      Read as UTF-8; CRLF line endings and box-drawing separator lines are tolerated.
    output: >
      dict with keys:
        meta      — dict of header fields (title lines, document reference, version, effective date)
        sections  — ordered list of {number, title, clauses}
        clauses   — ordered list of {id, section, text}, where text is the clause
                    reproduced verbatim with line-wrap whitespace collapsed to
                    single spaces and nothing else altered
        clause_ids — ordered list of every clause id found, used as the completeness
                    ground truth for the verification block
    error_handling: >
      File not found or unreadable → message to stderr, exit code 1; no output file
      is written. Zero parsable clauses → exit code 1 with the reason, because an
      empty-but-well-formatted summary is more dangerous than a visible failure.
      A continuation line appearing before any clause id → attached to the section
      header rather than silently discarded. Clause ids are never renumbered or
      reordered; source order is the contract.

  - name: classify_clause
    description: >
      Labels a clause with its binding verb classes, its extracted conditions, and
      whether it must be reproduced verbatim — the analysis that the summary sections
      are built from.
    input: "clause dict from retrieve_policy — {id, section, text}."
    output: >
      dict with keys:
        verb_classes  — list from PROHIBITION, MUST, REQUIRES, WILL, FORFEIT, MAY,
                        ENTITLEMENT, STATEMENT; all that apply, not just the strongest,
                        so clause 2.6 keeps both MAY and FORFEIT
        conditions    — list of str, each an exact substring of the clause: conjoined
                        approvers (split one per condition), time limits, thresholds,
                        preconditions, negated alternatives, forfeitures, scope
                        qualifiers; conditions nested inside a longer capture are
                        dropped as duplicates, keeping the longer one
        verbatim_required — bool
        verbatim_reason   — str, why compression was refused (critical clause,
                        multi-condition, or absolute qualifier)
    error_handling: >
      A clause matching no verb pattern is classed STATEMENT rather than guessed at,
      and still appears in the full clause record — unclassified never means omitted.
      Condition extraction returns exact source substrings only; if a pattern cannot
      be matched cleanly the whole clause is marked verbatim_required, which fails
      safe toward showing the reader more rather than less.

  - name: summarize_policy
    description: >
      Takes the structured sections and produces the compliant summary text with a
      clause reference on every line that makes a claim.
    input: >
      the dict returned by retrieve_policy, plus the per-clause analysis from
      classify_clause.
    output: >
      str — the summary document, in six blocks: AT A GLANCE (every figure tagged
      with its source clause), BINDING OBLIGATIONS INDEX, MULTI-CONDITION OBLIGATIONS
      (each condition on its own numbered line), ABSOLUTE PROHIBITIONS, FULL CLAUSE
      RECORD (verbatim, [VERBATIM-REQUIRED] marked), and VERIFICATION.
    error_handling: >
      Binding clause text is never paraphrased, so obligation softening cannot occur
      at this step. Before returning, the summary is checked against the source
      clause ids; any clause not cited is reported in the verification block and the
      run exits non-zero rather than writing a quietly incomplete file.

  - name: check_scope_bleed
    description: >
      Mechanically detects information the summariser added that is not in the source
      document — the testable form of "do not hallucinate".
    input: "summary_text (str) and the raw source text (str)."
    output: >
      list of str — words present in the summary's claim lines (those citing a clause
      id) but absent from both the source vocabulary and the declared structural
      template vocabulary. Headings are not audited because they assert nothing about
      the policy. Empty list means no scope bleed. The result is written into the summary's own verification block, so
      the check travels with the artefact instead of living only in the test run.
    error_handling: >
      Comparison is case-insensitive on alphabetic tokens of three or more characters;
      digits, punctuation and clause ids are excluded from the check rather than
      producing noise. The template vocabulary is a fixed declared constant in app.py,
      not a growing allowlist — adding a word to it is a visible code change a reviewer
      can object to, which is the point.