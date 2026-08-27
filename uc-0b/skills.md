# skills.md — UC-0B

skills:
  - name: retrieve_policy
    description: >
      Loads a policy .txt file, splits it into numbered clauses, and
      returns a structured representation preserving the original
      wording of every clause.
    input: >
      path (str) — filesystem path to a plaintext policy file whose
      body is organised as section headings followed by numbered
      clauses of the form N.M.
    output: >
      A dict {"header": {...meta fields...}, "sections": [
        {"number": "2", "title": "ANNUAL LEAVE",
         "clauses": [{"number": "2.1", "text": "..."}, ...]},
        ...
      ]}. The full text of every clause is preserved.
    error_handling: >
      If the file is missing or unreadable, raise a clear error and
      exit non-zero. If no numbered clauses are found, exit with a
      message rather than emitting an empty summary.

  - name: summarize_policy
    description: >
      Takes the structured policy from retrieve_policy and produces a
      compliance-safe summary in which every numbered clause is present,
      binding verbs are preserved, and multi-condition rules keep every
      condition. Adds no facts, no hedging, no generic phrasing.
    input: >
      A structured policy dict (as returned by retrieve_policy).
    output: >
      A single string suitable for writing to summary_hr_leave.txt.
      Each section is a block; each clause is one line prefixed with
      its number and its detected binding verb tag.
    error_handling: >
      If a clause contains multiple binding verbs or a construction the
      summariser cannot compact without meaning loss, that clause is
      emitted verbatim under a [VERBATIM — do not paraphrase] marker.
      Never drop or reword a clause silently.
