# skills.md

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from disk and returns its content as a dict of
      structured numbered sections keyed by clause number (e.g. "2.3", "5.2"),
      plus the full raw text and document metadata.
    input: >
      path (str) — absolute or relative path to the .txt policy file.
    output: >
      dict with three keys:
        raw      (str)        — full verbatim text of the document
        sections (dict[str, str]) — clause number → full clause text,
                                    e.g. {"2.3": "Employees must submit...", ...}
        metadata (dict[str, str]) — title, reference, version, effective date
                                    extracted from the document header block
    error_handling: >
      Raises FileNotFoundError if the path does not exist.
      Raises ValueError if the file is empty or no numbered clauses are detected.
      Both errors propagate to app.py which prints a clear message and exits 1.

  - name: summarize_policy
    description: >
      Takes structured policy sections from retrieve_policy and produces a
      compliance-grade summary with every clause from the Mandatory Clause
      Registry present, conditions intact, and binding verbs preserved.
      Supports two modes: 'naive' (single-pass baseline, expected to fail) and
      'enforced' (two-pass pipeline with summarize_agent + verify_agent).
    input: >
      structured (dict) — output of retrieve_policy.
      mode (str)        — "naive" or "enforced".
                          Defaults to "enforced" if omitted.
    output: >
      dict with five keys:
        summary      (str)          — the clause-by-clause summary text
        verification (str)          — verify_agent audit report (empty in naive mode)
        verdict      (str)          — "PASS", "FAIL", or "UNVERIFIED" (naive)
        mode         (str)          — "naive" or "enforced"
        retries      (int)          — number of Pass-1 retries needed (0 = clean)
    error_handling: >
      Naive mode: no validation; returns raw API output regardless of quality.
      Enforced mode: if verification fails after 2 retries, appends [UNRESOLVED]
      flags to failing clauses, includes the full verification report in the
      output file, and exits with status code 1 so CI/CD can catch it.
      API errors (auth, timeout, rate limit) are caught and re-raised with a
      descriptive message that includes the original error.