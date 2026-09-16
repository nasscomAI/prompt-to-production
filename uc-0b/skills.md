# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns it as structured numbered sections and
      clauses, preserving clause numbers, section titles and sentence boundaries.
    input: >
      path (str) — path to data/policy-documents/policy_*.txt
      Expected shape: a header block, then sections introduced by a rule line and
      a `N. TITLE` heading, then clauses matching `^N.M  text` with hanging-indent
      continuation lines.
    output: >
      dict:
        meta     — {"source": filename, "header": [first header lines]}
        sections — ordered list of {"number": "2", "title": "ANNUAL LEAVE",
                    "clauses": [...]}
        clauses  — ordered list of {"id": "2.4", "section": "2",
                    "text": unwrapped single-line clause text,
                    "sentences": [sentence, ...]}
      Clause order and clause numbering are preserved exactly as in the file.
      No text is altered beyond joining hard-wrapped lines and collapsing runs of
      whitespace — every returned sentence remains a substring of the source.
    error_handling: >
      - file missing / unreadable / not UTF-8 -> raises a clear error; the caller
        exits non-zero without writing any output.
      - zero clauses parsed (wrong file shape) -> raises rather than returning an
        empty structure, so a silent empty summary can never be produced.
      - clause text before any section heading -> attached to a synthetic section
        "0" rather than dropped.
      - duplicate clause ids -> kept in order and reported; deduplication is not
        this skill's job.

  - name: summarize_policy
    description: >
      Takes the structured sections and produces a clause-referenced compliance
      summary, enumerating every condition per clause and quoting verbatim any
      clause that cannot be compressed without dropping one.
    input: >
      structured (dict) — the output of retrieve_policy.
    output: >
      (summary_text, report) where summary_text contains, per clause:
        [2.4] MUST  [VERBATIM — multi-condition]
          <body: verbatim source sentences, unwrapped>
          conditions: written approval · direct manager · before the leave
                      commences · verbal approval NOT valid
      and report is a dict of counts (clauses_in, clauses_out, flagged,
      compression_ratio). Body text is EXTRACTIVE — every emitted sentence is a
      verbatim substring of the source, so obligations cannot be softened and
      outside information cannot be introduced.
    error_handling: >
      - a clause whose binding verb cannot be identified -> tagged CLAUSE rather
        than guessed, and included in full.
      - a clause with 2+ independent conditions -> not compressed at all; emitted
        verbatim with the [VERBATIM — multi-condition] flag, per enforcement.
      - never drops a clause for any reason; there is no failure mode in which a
        clause is omitted rather than flagged.

  - name: verify_summary
    description: >
      Adversarially checks the produced summary against the source and against the
      README's 10 ground-truth clauses, returning pass/fail per enforcement rule.
    input: >
      structured (dict), summary_text (str)
    output: >
      dict of check name -> list of violations (empty list == pass). Checks:
        clause_coverage     — every source clause id present in the summary
        extractive_fidelity — every summary body sentence is a source substring
        numeric_fidelity    — every numeric token per clause survives
        negation_fidelity   — every negation per clause survives
        ground_truth        — the 10 README clauses and their key conditions,
                              including BOTH approvers on 5.2
        scope_bleed         — no banned phrase appears in the output
      Prints a readable report to stdout.
    error_handling: >
      Never silently passes. Any non-empty violation list causes the caller to
      print the violations and exit non-zero, so an unverified summary is never
      presented as verified. The summary file is still written, so the failure can
      be inspected rather than guessed at.
