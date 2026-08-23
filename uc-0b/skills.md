# skills.md — UC-0B HR Leave Policy Summariser

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and returns it as structured data — document header lines, ordered sections, and every numbered clause with its exact source text.
    input: Path string to a UTF-8 .txt policy document using the CMC layout — banner-divided ALL-CAPS section headings ("2. ANNUAL LEAVE") and clauses beginning with decimal numbers ("2.3 Employees must...").
    output: Dict with keys "meta" (header lines before the first section), "sections" (ordered list of {"number", "title", "clauses"} where each clause is {"id", "text", "verbatim_required"}), and "clause_ids" (ordered list of every clause id found). Clause text is whitespace-normalised but otherwise character-for-character from the source.
    error_handling: Missing or unreadable input surfaces as a non-zero exit with a clear message — never as an empty document; a file that parses to zero sections or zero clauses raises PolicyParseError so the caller refuses instead of summarising garbage; wrapped clause continuation lines are joined into the owning clause without altering any words, and unrecognised non-blank lines inside a section are kept attached to the preceding clause rather than dropped.

  - name: summarize_policy
    description: Renders the structured policy into a compliant summary that preserves every clause number, every obligation, and every multi-condition requirement, plus a completeness ledger.
    input: The structured dict returned by retrieve_policy.
    output: Summary text for a UTF-8 .txt file — source-derived header, every section heading, every clause quoted in full with its number (compound-obligation clauses tagged [VERBATIM]), and a trailing completeness ledger reporting clauses rendered versus extracted, flagged clause ids, and 10/10 critical-clause verification. Also returns ledger stats for stdout reporting.
    error_handling: If any of the ten critical clause ids (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) are absent from the input structure it returns an error so the caller exits non-zero instead of writing a partial summary; if a section parsed with no clauses it is listed with an explicit "(no clauses parsed)" note rather than dropped silently; rendering is pure string assembly with no randomness or clock reads.
