# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content parsed into ordered, numbered sections ready for clause-by-clause processing.
    input: >
      A single file path (string) pointing to a plain-text policy document
      (e.g. policy_hr_leave.txt).
    output: >
      A list of dicts, one per numbered section found in the document:
        section_id  — the clause number as it appears in the source (e.g. "2.3", "5.2")
        heading     — the section heading text, if present; empty string if absent
        body        — the full verbatim text of that section
      Sections are returned in document order. The raw full-text string is also
      returned alongside the list for verbatim-quote fallback in summarize_policy.
    error_handling: >
      If the file path does not exist, raise FileNotFoundError with the path.
      If the file is empty or contains no recognisable numbered sections,
      raise ValueError stating: "No numbered clauses found in <filename> —
      verify the document format before summarising."
      Never return partial content without flagging that sections may be missing.

  - name: summarize_policy
    description: Takes the structured sections produced by retrieve_policy and returns a clause-faithful plain-language summary that preserves every obligation, binding verb, and multi-condition requirement exactly as stated in the source.
    input: >
      Two values:
        sections    — the list of section dicts returned by retrieve_policy
        source_text — the raw full-text string returned by retrieve_policy,
                      used for verbatim-quote fallback
    output: >
      A plain-text summary where:
        - Every numbered clause from sections is represented, in order,
          prefixed by its section_id (e.g. "2.3 — ...")
        - Binding verbs (must, will, requires, not permitted) are preserved
          exactly — never softened to "should", "may", or "is expected to"
        - Multi-condition obligations list ALL conditions explicitly
          (e.g. "requires Department Head AND HR Director approval")
        - Any clause that cannot be paraphrased without meaning loss is
          quoted verbatim from source_text and appended with [VERBATIM]
        - No sentence appears in the output that is not traceable to a
          specific clause in the source document
    error_handling: >
      If sections is empty, refuse and return: "No clauses to summarise —
      retrieve_policy must be called successfully first."
      If a section body is blank or unparseable, include the clause in the
      output as: "<section_id> — [VERBATIM] <raw body text>" rather than
      skipping it or guessing its meaning.
      Never omit a clause silently — a missing clause is a critical failure
      per agents.md enforcement rules.
