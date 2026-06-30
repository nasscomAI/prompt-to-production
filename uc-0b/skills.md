# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns it as structured, numbered sections and clauses.
    input: >
      path (str) — path to a policy .txt file whose sections are numbered
      headings (e.g. "2. ANNUAL LEAVE") and whose clauses are numbered
      "X.Y" (e.g. 2.3), with wrapped continuation lines.
    output: >
      An ordered list of sections, each a dict {number, title, clauses}, where
      every clause is {id, text} and text is the clause's full source wording
      with line wraps normalised. No clause is dropped or reordered.
    error_handling: >
      If the file is missing or unreadable, raise a clear error. Lines that match
      no clause/section/divider pattern are attached to the current clause as
      continuation rather than discarded, so no source text is lost.

  - name: summarize_policy
    description: Turns structured sections into a compliant summary with clause references, verbatim-quoting and flagging high-risk clauses.
    input: >
      sections (the structure from retrieve_policy) plus a critical-clause config
      mapping high-risk clause ids to the condition tokens that must survive
      (e.g. 5.2 -> ["Department Head", "HR Director"]).
    output: >
      Summary text where every clause id appears with its obligation, binding
      verbs preserved, critical clauses flagged and quoted verbatim with their
      conditions enumerated, plus a compliance report listing any clause that is
      missing, any dropped condition, and any scope-bleed phrase detected.
    error_handling: >
      If a critical clause's required condition tokens are not all present, the
      verifier fails loudly (non-zero exit) rather than emitting a summary that
      has silently dropped a condition. Scope-bleed phrases, if ever present,
      fail the same check.
