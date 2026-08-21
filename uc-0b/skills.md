# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a single .txt policy file and returns it as structured, numbered
      sections and clauses, discarding decorative separators and carrying the
      document header block as metadata rather than as content.
    input: >
      path (str) — filesystem path to one .txt policy document. Exactly one file.
      Multiple paths are rejected; this skill never loads a second document.
    output: >
      dict with keys:
        meta      — list[str], the header block lines (org, department, doc ref, version)
        sections  — list of {number: str, title: str, clauses: list of
                    {id: str, text: str, sentences: list[str]}}
      Clause text has line-wrap artefacts removed; sentence boundaries are preserved
      so that downstream condition enumeration is possible.
    error_handling: >
      File missing or unreadable → raise PolicyError with the path; caller exits
      non-zero. File parses to zero clauses → raise PolicyError rather than
      returning an empty structure, because an empty parse silently produces an
      empty summary that passes every downstream check. A line that looks like a
      clause but has no text is kept with empty text and flagged, never dropped.

  - name: summarize_policy
    description: >
      Takes the structured sections from retrieve_policy and produces a compliant
      clause register — every clause under its own ID, binding verb named, all
      conditions enumerated — then validates the register against the source before
      returning it.
    input: >
      structured (dict) — the output of retrieve_policy.
      strict (bool) — when True, a failed validation raises instead of returning.
    output: >
      tuple (summary_text: str, report: dict).
      report contains: clauses_source, clauses_summary, missing_ids, extra_ids,
      token_failures (per clause), flagged_verbatim (list of ids), banned_phrases
      (list of hits), critical_gate (pass/fail on the 10 asserted clause IDs),
      and ok (bool).
    error_handling: >
      A clause whose critical tokens would not survive condensing is NOT paraphrased —
      it is emitted verbatim and flagged VERBATIM-REQUIRED, and the run continues.
      A missing clause ID, an extra clause ID, or a banned phrase is not recoverable:
      report.ok is False and, under strict, SummaryError is raised so the run exits
      non-zero rather than writing a summary that looks finished. The validator runs
      against the rendered text, not against the intermediate structure, so a bug in
      rendering cannot pass validation.

  - name: validate_summary
    description: >
      Internal check used by summarize_policy and runnable on its own against any
      candidate summary — including one produced by a different tool — to test
      whether it drops clauses, drops conditions, or adds unsourced language.
    input: >
      structured (dict) from retrieve_policy, candidate_text (str).
    output: >
      report (dict), same shape as above.
    error_handling: >
      Never raises on content; it reports. Its job is to describe the failure
      precisely enough to name the failure mode — clause omission, condition drop,
      or scope bleed — so the fix can be targeted at one enforcement rule.
