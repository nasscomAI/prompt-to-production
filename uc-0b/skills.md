skills:
  - name: retrieve_policy
    description: Loads a numbered .txt policy file from disk and returns it as an ordered list of clauses keyed by clause number, so downstream summarisation can iterate clause-by-clause rather than over free text.
    input: |
      path: str — absolute or relative path to a UTF-8 .txt policy file
      structured per the CMC HR-POL convention (sections delimited by
      "═══" rules; clauses numbered N.M at the start of a line).
    output: |
      list[dict] in source order, each entry:
        { "clause": "2.3",
          "section": "ANNUAL LEAVE",
          "text": "Employees must submit a leave application at least
                   14 calendar days in advance using Form HR-L1." }
      Multi-line clauses are joined into a single text field with
      single spaces; original line breaks inside a clause are not
      preserved. Section headers without a clause number are not
      emitted as entries — they only populate the `section` field of
      following clauses.
    error_handling: |
      - File missing or unreadable → raise FileNotFoundError /
        PermissionError; do not return a partial list.
      - File present but contains zero clauses matching the N.M
        pattern → raise ValueError("no numbered clauses found");
        the caller is expected to surface this and exit non-zero.
      - Duplicate clause number in the source → raise
        ValueError(f"duplicate clause {n}"); do not silently merge or
        overwrite — duplicates indicate a corrupt source.
      - Malformed clause numbers (e.g. "2.3.1" or "2-3") → preserve
        verbatim in the `clause` field; do not normalise. The
        summariser decides what to do with them.

  - name: summarize_policy
    description: Takes the structured clause list from retrieve_policy and produces a fidelity-preserving summary string in which every clause appears exactly once verbatim, prefixed by its clause number and (when applicable) by the binding verb(s) governing that clause in square brackets — the tag IS the verb, not a generic flag.
    input: |
      clauses: list[dict] as returned by retrieve_policy.
    output: |
      str — newline-separated summary. Each line begins with the
      clause number followed by the verbatim source text. If the
      clause carries one or more binding verbs, they are inserted
      between the clause number and the text in the form
      "[verb1 / verb2]". The tag is the binding verb itself, mirroring
      the "Binding verb" column in README.md. Examples:
        "2.3 [must] Employees must submit a leave application at
             least 14 calendar days in advance using Form HR-L1."
        "5.2 [requires / not sufficient] LWP requires approval from
             the Department Head and the HR Director. Manager
             approval alone is not sufficient."
        "2.6 [may / are forfeited] Employees may carry forward a
             maximum of 5 unused annual leave days to the following
             calendar year. Any days above 5 are forfeited on 31
             December."
        "1.1 This policy governs all leave entitlements ..."   # no tag
      Allowed verb labels: must, will, requires, may, cannot,
      are forfeited, mandatory, reserves the right, entitled,
      required, permitted, reimbursable, not permitted,
      not reimbursable, not eligible, not valid, not accepted,
      not allowed, not sufficient, not considered, only if, provided,
      does not apply, does not cover.
      Multiple verbs in one clause are joined by " / " in source
      order. Section headers (e.g. "## ANNUAL LEAVE") are emitted
      between clause groups, carried over from the source.
      Clause body text is never paraphrased or shortened.
    error_handling: |
      - Empty clause list → raise ValueError("no clauses to
        summarise"); do not return an empty string (which a caller
        could mistake for a successful empty summary).
      - A clause whose binding verb cannot be identified from the
        allowed-label set → emit the clause untagged but still
        verbatim. Do not invent a verb that is not present in the
        source.
      - Overlapping verb matches in a single clause (e.g. "permitted"
        inside "not permitted") → resolve to the longest span at each
        position so that "not permitted" wins over a bare "permitted".
        Each canonical label appears at most once per clause.
