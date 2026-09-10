# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return its content as structured numbered sections with document metadata.
    input: `path` (string, path to a UTF-8 .txt policy file with numbered clauses like `2.3`).
    output: A dict with `meta` (document reference, version, effective date as found in the header lines) and `sections` (ordered list of `{number, title, clauses}`, each clause `{number, text}` with whitespace-normalized full source text, in document order).
    error_handling: Raises FileNotFoundError with a clear message if the path does not exist; raises ValueError if no numbered clauses can be parsed. Never invents clause numbers or text — only what the regex parses from the file.

  - name: summarize_policy
    description: Render structured policy sections into a compliant clause-referenced summary that preserves every clause, condition, and binding verb.
    input: The structured dict returned by retrieve_policy.
    output: A plain-text summary string: header (source ref/version/effective date), one bullet per numbered clause in order starting with `[X.Y]`, critical clauses rendered with full source text, plus a trailing `Coverage:` line listing clause count and a `QUOTE-FLAG:` line for verbatim clauses. Every bullet is traceable to its source clause; no external information is added.
    error_handling: Never drops a clause silently — if a clause has empty text it is emitted verbatim as `[X.Y] (source text unavailable — see source)` and its number is added to QUOTE-FLAG. Never emits banned scope-bleed phrases or softened binding verbs; output uses only source-derived wording.
