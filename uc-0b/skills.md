# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt leave policy file, cleans formatting noise, and
      extracts the 10 required clauses into a keyed dictionary.
    input: File path string pointing to a UTF-8 encoded .txt policy document.
    output: Dict[str, str] mapping each required clause ID (e.g. "2.3") to its
      extracted body text; empty string if clause not found in document.
    error_handling: Raises PolicyError if file does not exist, file is empty,
      or no clause IDs are extractable after cleaning and normalization.

  - name: summarize_policy
    description: Takes the extracted clause dictionary, validates each clause,
      and produces a structured compliance summary with omission and risk reports.
    input: Dict[str, str] returned by retrieve_policy — clause IDs mapped to
      their body text.
    output: Formatted multi-section string containing clause summaries, omission
      report, validation risk report, and final compliance status (PASS /
      REVIEW REQUIRED).
    error_handling: Raises PolicyError if any vague phrase (typically, generally,
      usually, standard practice) is detected in the assembled output; flags
      missing clauses as [CLAUSE NOT FOUND IN DOCUMENT — manual verification
      required] and flags clause 5.2 missing dual-approval as [VERBATIM —
      condition-drop risk] rather than silently passing.