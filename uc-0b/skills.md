skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file from a given path and returns its content
      parsed into structured numbered sections keyed by clause number.
    input:
      type: string
      format: >
        Absolute or relative file path pointing to a .txt policy document.
        Expected value for this use case: ../data/policy-documents/policy_hr_leave.txt
    output:
      type: list of objects
      format: >
        Ordered list of section objects, each containing:
          clause_number (string, e.g. "2.3"),
          heading (string, the section title if present),
          body (string, the full verbatim text of that clause).
        All 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2,
        5.3, 7.2) must be present as discrete entries if they exist in the file.
    error_handling:
      - If the file path does not exist or cannot be read, raise a
        FileNotFoundError with the exact path attempted; do not continue.
      - If the file is not a .txt file, raise a TypeError and halt; do not
        attempt to parse binary or non-text formats.
      - If the file is empty, raise a ValueError stating the file is empty;
        do not return an empty list silently.
      - If numbered clause markers cannot be detected (file lacks structured
        numbering), return the full raw text as a single section with
        clause_number set to "UNSTRUCTURED" and flag a warning that
        clause-level verification will not be possible.
      - Never infer, reorder, or merge clause content; return only what is
        present verbatim.

  - name: summarize_policy
    description: >
      Takes the structured numbered sections produced by retrieve_policy and
      produces a clause-complete, obligation-preserving summary with explicit
      clause references suitable for writing to summary_hr_leave.txt.
    input:
      type: list of objects
      format: >
        The exact output structure from retrieve_policy — an ordered list of
        section objects each with clause_number, heading, and body fields.
        Must not be empty and must contain at minimum the 10 mandatory clause
        entries (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
    output:
      type: string
      format: >
        Plain-text summary written to uc-0b/summary_hr_leave.txt. Each clause
        is represented as a labelled paragraph beginning with its clause number
        (e.g. "Clause 2.3:"). Binding verbs (must, will, requires, not
        permitted) are reproduced exactly as they appear in the source.
        Multi-condition obligations list every condition explicitly on the same
        line. Where paraphrase would lose meaning, the clause body is quoted
        verbatim and tagged [VERBATIM — paraphrase would lose meaning].
    error_handling:
      - If any of the 10 mandatory clauses is absent from the input list,
        raise a ValueError naming the missing clause numbers and halt; do not
        produce a partial summary.
      - If a clause body contains a multi-condition obligation (detected by
        conjunctions such as "AND", "and", "as well as" joining named roles or
        thresholds), verify all conditions are reproduced in the output; if
        any condition would be dropped, quote verbatim and apply the VERBATIM
        flag instead of summarising.
      - If the generated summary text contains any phrase not traceable to the
        source sections (scope bleed detection: phrases like "as is standard
        practice", "typically in government organisations", "employees are
        generally expected to"), remove the phrase and log a scope-bleed
        warning before writing output.
      - If a binding verb in the source (must, will, requires, not permitted)
        would be rendered as a weaker form (should, may, is recommended,
        discouraged) in the summary, replace it with the original binding verb
        and log an obligation-softening warning.
      - Never produce output from sources other than the input sections list;
        do not consult external knowledge or defaults.
