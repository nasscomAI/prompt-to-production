skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file from disk and returns its content
      parsed into an ordered list of numbered sections, preserving all clause
      numbers, binding verbs, and condition language exactly as written.
    input:
      type: string
      format: Absolute or relative file path pointing to a .txt policy document;
        expected to contain numbered clauses in hierarchical decimal notation
        (e.g. 2.3, 5.2).
    output:
      type: list
      format: Ordered list of objects, each containing clause_number (string),
        clause_text (string, verbatim from source), and binding_verb (string,
        extracted from clause_text); list order matches document order.
    error_handling:
      file_not_found: Halt and return an error object with code FILE_NOT_FOUND
        and the attempted path; do not proceed to summarize_policy.
      unreadable_or_non_txt: Halt and return error code UNSUPPORTED_FORMAT; do
        not attempt to parse binary or non-plain-text content.
      no_numbered_clauses_detected: Return error code NO_CLAUSES_DETECTED and
        the raw file content; flag that structured parsing failed so the caller
        can inspect the file manually before proceeding.
      partial_clause_numbering: Return all parseable clauses plus a
        PARTIAL_PARSE warning listing any line ranges that could not be assigned
        a clause number; do not silently discard unparsed lines.

  - name: summarize_policy
    description: Takes the structured clause list produced by retrieve_policy and
      generates a clause-complete, obligation-faithful summary that references
      every clause by number, preserves all conditions and binding verbs, and
      contains no information absent from the source document.
    input:
      type: list
      format: The exact output of retrieve_policy — an ordered list of objects
        each containing clause_number, clause_text, and binding_verb; no other
        input source is permitted.
    output:
      type: string
      format: Plain-text summary with one entry per clause in document order;
        each entry prefixed by its clause number; binding verbs preserved
        verbatim or with a direct legal-force equivalent; any clause that cannot
        be condensed without meaning loss is reproduced verbatim and appended
        with the flag [VERBATIM - meaning-loss risk]; written to
        uc-0b/summary_hr_leave.txt.
    error_handling:
      missing_clause_in_input: If any of the 10 expected clauses (2.3, 2.4,
        2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are absent from the input
        list, halt and return error code INCOMPLETE_CLAUSE_LIST naming the
        missing clause numbers; do not produce a partial summary.
      condition_drop_detected: Before writing output, run a self-check on
        multi-condition clauses; if clause 5.2 does not name both Department
        Head and HR Director, or clause 5.3 does not name Municipal
        Commissioner, abort with error code CONDITION_DROP and identify the
        affected clause.
      scope_bleed_detected: If any generated sentence contains language not
        traceable to the input clause_text fields — including phrases such as
        "as is standard practice", "typically in government organisations", or
        "employees are generally expected to" — remove the sentence, log a
        SCOPE_BLEED warning identifying the offending phrase, and regenerate
        that clause entry before writing output.
      binding_verb_softened: If a binding verb is replaced with a weaker modal
        (e.g. "should" for "must", "may wish to" for "requires") flag the
        clause with OBLIGATION_SOFTENING and restore the original verb before
        writing output.
      meaning_loss_on_condensation: If condensing any clause produces ambiguity
        or omits a qualifier, quote the clause verbatim from clause_text and
        append [VERBATIM - meaning-loss risk] rather than producing an
        inaccurate paraphrase.