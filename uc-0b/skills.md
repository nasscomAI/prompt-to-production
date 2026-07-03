skills:
  - name: retrieve_policy
    description: >
      Loads a plain-text policy file, splits it into numbered sections by
      detecting clause headers (e.g. "2.3", "3.4"), and returns the content
      as an ordered list of structured section objects ready for summarisation.
    input: >
      A file-path string pointing to the policy .txt file
      (e.g. "../data/policy-documents/policy_hr_leave.txt").
      The file is expected to be UTF-8 plain text with clause numbers in the
      format <section>.<clause> (e.g. 2.3, 5.2) at the start of a line or
      paragraph.
    output: >
      An ordered list of section dicts, one per detected clause, each
      containing:
        - clause_id   (string): the clause number exactly as it appears in the
          file (e.g. "2.3", "5.2").
        - heading     (string): the parent section title
          (e.g. "ANNUAL LEAVE", "LEAVE WITHOUT PAY").
        - text        (string): the full verbatim text of that clause,
          whitespace-normalised, with no words added or removed.
      Clause order matches the document order. All 10 target clauses
      (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) must be present in
      the output list; if any are absent from the file, they are reported in
      the missing_clauses field (see error_handling).
    error_handling: >
      - If the file does not exist or cannot be opened: raise FileNotFoundError
        with the full path in the message; do not return a partial result.
      - If the file is empty or contains no detectable clause numbers: raise
        ValueError("No numbered clauses found in <path>"); do not return an
        empty list silently.
      - If any of the 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2,
        3.4, 5.2, 5.3, 7.2) are absent from the parsed output, return the
        list of successfully parsed clauses AND a separate missing_clauses
        list; do not silently omit the warning.
      - Never infer or reconstruct clause text that is not present in the file;
        if a clause boundary is ambiguous, include all text up to the next
        detected clause number.

  - name: summarize_policy
    description: >
      Takes the structured section list produced by retrieve_policy and
      generates a clause-level policy summary that preserves every obligation,
      condition, and binding verb exactly as mandated by agents.md, with no
      omissions, softening, or externally sourced additions.
    input: >
      The ordered list of section dicts returned by retrieve_policy, where
      each dict contains clause_id (string), heading (string), and text
      (string — verbatim clause content).
    output: >
      A plain-text summary string structured as one entry per clause, in
      document order, using the format:

        [<clause_id>] <heading> — <summary sentence(s)>

      Constraints enforced on every entry:
        - The clause_id must match the source exactly (e.g. "Clause 2.4",
          not "Section 2.4" or "2.4.").
        - All conditions in multi-condition clauses must be preserved.
          For clause 5.2 specifically, both "Department Head" and "HR Director"
          must be named; no aggregated phrase (e.g. "senior management",
          "dual approval") is permitted.
        - Binding verbs (must, will, requires, not permitted, are forfeited)
          must appear unchanged; they may not be replaced with softer modals
          such as "should", "may", or "is expected to".
        - No phrase may appear in the output that is not traceable to a
          sentence in the source clause text. Phrases such as "as is standard
          practice", "typically in government organisations", or "employees are
          generally expected to" are explicitly prohibited.
        - All 10 target clauses must be present in the output, each identified
          by its clause number.
    error_handling: >
      - If the input list is empty or None: raise ValueError("No clauses
        provided to summarize_policy; run retrieve_policy first.").
      - If any of the 10 mandatory clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2,
        3.4, 5.2, 5.3, 7.2) is not present in the input list: append a
        clearly labelled warning block at the end of the summary:
          [WARNING] The following mandatory clauses were not found in the
          source document and could not be summarised: <list>
        Do not invent or reconstruct the missing clause content.
      - If a clause cannot be summarised in fewer words without risk of
        meaning loss (e.g. due to multiple tightly coupled conditions): quote
        the clause verbatim and append the flag:
          [VERBATIM — cannot be shortened without meaning loss]
      - Never silently drop a clause, condition, or binding verb; always
        prefer flagging over guessing.
