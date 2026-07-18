# skills.md — UC-0B

These are the two deterministic skills the summarization agent composes to
turn a raw policy file into a faithful summary. Both are pure standard-library
Python, rule-based, and side-effect-free apart from reading the input file and
writing the output file. No LLM, no network, no third-party packages.

---

## retrieve_policy

description
    Load a single policy .txt file and return its content as an ordered set of
    numbered sections, each carrying its numbered clauses. This is the ONLY
    skill allowed to touch the source file; everything downstream consumes its
    structured output, so no later stage can accidentally re-introduce raw or
    out-of-scope text.

input
    A path (str or pathlib.Path) to a UTF-8 .txt policy file. The document is
    expected to contain top-level sections headed `N. TITLE` (all-caps) and
    clauses of the form `N.N <prose>`, with continuation lines indented and
    sections separated by box-drawing rules.

output
    A tuple (header_lines, sections) where:
      - header_lines is a list[str] of document metadata captured above the
        first section (title, reference, version/effective date).
      - sections is an ordered list of dicts:
            {
              "section_id":   "2",
              "section_title":"ANNUAL LEAVE",
              "clauses": [
                {"id": "2.1", "text": "Each permanent employee is entitled to ..."},
                ...
              ]
            }
    Each clause's text is its original prose with continuation lines joined
    and whitespace collapsed to a single space — verbatim wording, no
    paraphrase, no dropped words. Clause ids within a section are contiguous
    from 1 to that section's maximum; a gap is treated as a parse failure.

error_handling
    - File missing or unreadable: raise / exit non-zero with the path and the
      reason. Never return an empty structure silently.
    - Zero numbered clauses parsed (wrong file / wrong format): exit non-zero
      with "no numbered clauses parsed — not a valid policy document".
    - A gap in clause numbering inside a section (e.g. section 2 jumps from
      2.4 to 2.6): exit non-zero naming the missing clause id(s) — a gap
      signals an omission that must be fixed at the source, not papered over.

---

## summarize_policy

description
    Turn the structured sections from retrieve_policy into a compliant
    human-readable summary that preserves every clause and every condition,
    each line tagged with its clause reference `[N.N]`. It reorganizes for
    readability (grouped by section, decoration stripped, lines joined) but
    never paraphrases a binding clause — paraphrasing is the root cause of
    condition drop and scope bleed, so it is structurally disallowed.

input
    The (header_lines, sections) structures produced by retrieve_policy.

output
    A summary string, also written to the output path. Layout:
      - A one-line title plus source metadata (reference, version) taken only
        from header_lines.
      - One block per section: the section heading, then one line per clause
        formatted `[N.N] <faithful clause text>`.
      - A `COMPLETENESS INDEX` footer listing every clause id, in order, so
        the every-clause-present rule is trivially auditable.

    The summary is self-audited before it is written:
      - FORBIDDEN scope-bleed phrases (as is standard practice, typically,
        usually, normally, generally, in most organisations/organizations,
        employees are generally expected to, as per company policy, it is
        understood that) must not appear; if any do, the tool refuses
        (exit 2) rather than ship an invented summary.
      - CRITICAL multi-condition clauses are asserted: clause 5.2 must contain
        BOTH "Department Head" and "HR Director"; clause 7.2 must contain "not
        permitted under any circumstances"; clause 2.6 must convey the 5-day
        cap and 31 December forfeiture; clause 2.4 must keep "Verbal approval
        is not valid"; clause 3.2 must keep "within 48 hours"; clause 5.3 must
        keep "Municipal Commissioner". A missing substring exits non-zero with
        the clause id and the missing phrase named.

error_handling
    - Any forbidden phrase detected in the generated output: exit 2 (scope
      bleed) with the offending phrase(s) listed.
    - Any critical-condition substring missing from its clause: exit 4
      (condition drop) naming the clause id and the missing phrase.
    - If a clause's text is empty after parsing (the source had an id with no
      body): tag it `[VERBATIM-EMPTY]` and refuse rather than fabricate a body.
