# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns it as structured numbered sections
      and clauses, with hard line wraps rejoined and document metadata extracted.
    input: >
      path (str) — path to a UTF-8 policy .txt whose sections are numbered
      "N. TITLE IN CAPS" and whose clauses are numbered "N.M clause text",
      with continuation lines indented.
    output: >
      dict:
        title    — str, document title lines above section 1
        reference— str, e.g. "HR-POL-001"
        version  — str, e.g. "2.3 | Effective: 1 April 2024"
        sections — list of {number: str, title: str, clauses: [...]}
        clauses  — flat list of {id: str, section: str, text: str} in source
                   order, text whitespace-normalised to one line
      Whitespace normalisation is the only transformation applied; no word is
      added, removed, or reordered inside a clause.
    error_handling: >
      Missing or unreadable file -> clear message on stderr, exit 1. A file with
      zero parseable clauses -> exit 1 rather than emitting an empty summary,
      because an empty summary of a real policy is the most dangerous possible
      output. Lines that match neither a section header, a clause, a continuation,
      nor a divider are collected into an "unparsed" list and reported, so silent
      loss of source text is visible.

  - name: summarize_policy
    description: >
      Turns structured sections into a compliance summary — binding clauses
      verbatim with their binding verbs and enumerated conditions, informational
      clauses compressed to their extracted figures — then verifies its own
      output against the enforcement rules before returning it.
    input: >
      policy (dict) — the structure returned by retrieve_policy.
    output: >
      tuple (summary_text: str, report: dict). summary_text has four parts:
        COVERAGE            — clause counts in/out, binding and multi-condition tallies
        BINDING OBLIGATIONS — verbatim clause text, binding labels, numeric
                              limits, enumerated conditions with counts
        ENTITLEMENTS & SCOPE— non-binding clauses, compressed, figures retained
        VERIFICATION        — PASS/FAIL per enforcement rule
      report carries the same verification results as booleans plus the list of
      failures, so a caller can act on them without parsing text.
    error_handling: >
      Detects rather than hides its own failures. Runs four checks: clause
      count in == out; no banned hedging or scope-bleed phrase present; every
      alphabetic token traceable to the source or to STRUCTURAL_VOCABULARY; and
      all 10 critical clauses present with their required key phrases intact.
      On any failure it still writes the summary — with FAIL recorded in the
      verification block so the defect is on the record — prints the failures to
      stderr, and exits non-zero. It never reports a summary as complete
      without having proved it.
