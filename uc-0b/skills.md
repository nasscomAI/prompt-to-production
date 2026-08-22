# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy document from disk and parses it into a list of
      numbered sections, each with its section number and full text.
    input: >
      A string: file_path — the absolute or relative path to a .txt policy
      document structured with numbered sections (e.g. "1.1", "2.3").
    output: >
      A list of dicts, each with keys:
        section  (string, e.g. "2.3"),
        heading  (string, the section heading if present, else ""),
        text     (string, the full text of that section, whitespace-normalised).
      Sections are returned in document order.
    error_handling: >
      If the file does not exist, raise FileNotFoundError with a descriptive
      message. If the file is empty or contains no parseable numbered sections,
      raise ValueError("No numbered sections found in <file_path>").
      Never return a partial list for a truncated file — raise ValueError instead.

  - name: summarize_policy
    description: >
      Takes the structured section list from retrieve_policy and produces a
      clause-complete, obligation-preserving summary as a plain-text string.
    input: >
      A list of dicts as returned by retrieve_policy (keys: section, heading,
      text). Each dict represents one numbered clause.
    output: >
      A plain-text string. Format per clause:
        [section] [one-sentence summary citing binding verbs and all conditions]
      Multi-condition obligations are never simplified. Clauses that cannot be
      summarised without meaning loss are quoted verbatim and flagged with
      [VERBATIM — clause X.Y]. The final output ends with:
        "Summary complete. [N] clauses processed."
    error_handling: >
      If the input list is empty, return the string:
        "ERROR: No clauses to summarise. Check retrieve_policy output."
      If a single section dict is malformed (missing keys), skip it, log a
      warning to stderr with the section identifier, and continue. Never
      crash on a malformed row — always produce output for the remaining clauses.
