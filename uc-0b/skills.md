# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file from the specified path and returns its
      content parsed into structured numbered sections keyed by clause
      number.
    input:
      type: string
      format: >
        A file path pointing to a .txt policy document; expected path is
        ../data/policy-documents/policy_hr_leave.txt; the file must be
        UTF-8 encoded plain text containing numbered clauses in the format
        [section].[clause] followed by obligation text.
    output:
      type: object
      format: >
        A structured key-value mapping where each key is a clause identifier
        string (e.g. "2.3", "5.2") and each value is the verbatim clause
        text as it appears in the source file, with no modifications,
        additions, or paraphrasing; the object must contain entries for all
        clauses present in the document including at minimum 2.3, 2.4, 2.5,
        2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
    error_handling:
      file_not_found: >
        If the file path does not resolve to a readable file, halt and raise
        a descriptive error stating the expected path — do not return an
        empty or partial structure.
      unreadable_encoding: >
        If the file cannot be decoded as UTF-8, halt and raise an encoding
        error identifying the file — do not attempt lossy decoding that
        could corrupt clause text.
      no_clauses_detected: >
        If the parsed text yields no identifiable numbered clause structure,
        halt and raise a parse error rather than returning an empty object —
        a structureless return would cause summarize_policy to silently
        produce an empty summary.
      missing_required_clauses: >
        If any of the ten ground-truth clauses (2.3, 2.4, 2.5, 2.6, 2.7,
        3.2, 3.4, 5.2, 5.3, 7.2) are absent from the parsed output, emit a
        WARNING listing each missing clause number before returning — do not
        silently omit them, as downstream summarization would then produce
        an incomplete summary without a detectable signal.

  - name: summarize_policy
    description: >
      Takes the structured clause map produced by retrieve_policy and
      produces a compliant clause-by-clause summary that preserves all
      obligations, conditions, and binding verbs exactly as stated in the
      source, with each entry referenced by its clause number.
    input:
      type: object
      format: >
        The structured key-value clause map output by retrieve_policy, where
        keys are clause identifier strings and values are verbatim clause
        texts; must contain at minimum entries for clauses 2.3, 2.4, 2.5,
        2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2.
    output:
      type: file
      format: >
        A plain-text file written to uc-0b/summary_hr_leave.txt containing
        one summary entry per clause in clause-number order; each entry
        begins with the clause number, followed by a faithful summary that
        preserves all conditions and binding verbs; any clause that cannot
        be summarised without meaning loss is reproduced verbatim from the
        source and marked with the label DIRECT QUOTE.
    error_handling:
      empty_input: >
        If the input clause map is empty or missing, halt and raise an error
        — do not write an empty output file, as an empty summary is
        indistinguishable from a successful run with no clauses.
      missing_required_clause: >
        If any of the ten required clauses are absent from the input map,
        halt and raise an error listing the missing clause numbers rather
        than producing a summary known to be incomplete.
      condition_drop_detected: >
        If summarising a multi-condition clause would require dropping any
        condition — including the dual-approver requirement in clause 5.2
        or the verbal-invalid condition in clause 2.4 — the skill must quote
        that clause verbatim from the source and mark it DIRECT QUOTE rather
        than emit a summary with a silently dropped condition.
      obligation_softening_detected: >
        If the generated summary text for any clause replaces a binding verb
        (must, will, requires, are forfeited, not permitted) with a weaker
        modal such as should, may, is expected to, or is encouraged to, the
        skill must reject that draft, revert to the source verb, and flag the
        clause for human review before writing output.
      scope_bleed_detected: >
        If the summary text for any clause contains phrases not traceable to
        the source document — including "as is standard practice", "typically
        in government organisations", or "employees are generally expected to"
        — the skill must strip those phrases and rewrite the entry using only
        source-grounded language before writing output.
      meaning_loss_on_summarization: >
        If a clause cannot be condensed into a summary sentence without
        altering its legal or procedural meaning, the skill must fall back to
        verbatim quotation of that clause and append the label DIRECT QUOTE
        — partial or approximate rendering is not an acceptable fallback.
