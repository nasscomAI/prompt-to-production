# skills.md — UC-0B Policy Summariser

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered
      sections and clauses, preserving source order and the document's own
      reference metadata.
    input: >
      path (str) — path to a plain-text policy file whose sections are numbered
      "N. TITLE" and whose clauses are numbered "N.N " at the start of a line,
      with indented continuation lines.
    output: >
      A dict: {"metadata": {source_file, reference, version, effective, title},
      "sections": [{"number": "2", "title": "ANNUAL LEAVE",
      "clauses": [{"number": "2.3", "text": "<whitespace-normalised text>"}]}]}.
      Clause order is source order; no clause is merged, split, or reordered.
    error_handling: >
      File not found → raises FileNotFoundError naming the attempted path.
      File parses to zero clauses → raises ValueError and writes nothing, per
      the agents.md refusal condition (a prose summary of unstructured text is
      not an acceptable substitute). Clause text that spans continuation lines
      is joined with single spaces; a continuation line appearing before any
      clause number is attached to the section header, never to a clause.
      Unknown metadata fields are returned as empty strings rather than guessed.

  - name: summarize_policy
    description: >
      Takes the structured sections and produces a compliant, clause-referenced
      summary, gated by a condition-preservation check and a scope-bleed check
      before any line is accepted.
    input: >
      The dict returned by retrieve_policy.
    output: >
      A dict: {"lines": [str], "clause_count", "summarised_count",
      "omitted": [clause numbers], "verbatim": [clause numbers that fell back],
      "bleed": [words not found in the source],
      "multi_condition": {clause: [conditions retained]},
      "compression_ratio": float}. "lines" is the finished summary text.
    error_handling: >
      Condition-preservation gate — for each clause, conditions extracted from
      the source (quantities, deadlines, calendar dates, form numbers, named
      approvers, absolute qualifiers such as "under any circumstances") must
      all reappear in the candidate line. If any is missing, the candidate is
      discarded and the clause is emitted verbatim and recorded in "verbatim";
      the clause is never emitted lossily.
      Scope-bleed gate — every alphabetic word in the finished summary must
      occur in the source vocabulary or in STRUCTURAL_ALLOWLIST. Anything else
      is returned in "bleed" and the caller exits non-zero.
      Completeness gate — any clause parsed but not summarised is returned in
      "omitted" and the caller exits non-zero.
      Binding verbs are copied from the source, never re-worded; a clause with
      no recognised binding verb is tagged [STATES] rather than being assigned
      a strength it does not have.
