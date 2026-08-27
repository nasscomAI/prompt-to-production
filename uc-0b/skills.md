# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered clauses, reflowing each clause's wrapped lines into one line so nothing is lost before summarization.
    input: >
      file_path (str) — path to a policy .txt document with section headers
      (e.g. "2. ANNUAL LEAVE") and numbered clauses (e.g. "2.3 Employees must...").
    output: >
      A list of dicts, one per clause, each with keys: section (the enclosing
      section header), clause (the clause number, e.g. "2.3"), text (the full
      clause text with line-wrapping collapsed to a single line).
    error_handling: >
      If the file cannot be read, or no numbered clauses are found, raise an
      error rather than silently returning an empty result — a missing or
      unparseable source document is a boundary failure, not something to
      guess around.

  - name: summarize_policy
    description: Takes the structured clauses from retrieve_policy and produces the compliant summary — one line per clause, grouped by section, with the original wording preserved so no obligation, condition, or restriction can be softened or dropped.
    input: >
      The list of clause dicts returned by retrieve_policy.
    output: >
      A single string: the full summary text, with every clause from the
      source document present as "Clause X.Y: <clause text>" under its
      section heading, in document order.
    error_handling: >
      The summary never paraphrases a clause, so no clause can lose meaning
      in translation — every clause is carried through verbatim after
      whitespace/line-wrap normalization, which satisfies the "quote
      verbatim and flag" rule for every clause by construction rather than
      by detecting hard cases after the fact.
