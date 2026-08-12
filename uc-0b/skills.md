# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections and clauses, joining wrapped physical lines back into single logical clause sentences.
    input: file_path (str) — path to a policy .txt file with "N. SECTION NAME" headers and "N.N clause text" clauses (clause text may wrap across multiple indented physical lines).
    output: >
      A list of section dicts, each: {number: str, title: str,
      clauses: [{number: str, text: str}]}. `text` is the fully de-wrapped,
      whitespace-normalized clause sentence(s) — never a truncated
      fragment of a physical line.
    error_handling: >
      If the file does not exist or is empty, raises a clear error naming
      the missing/empty file rather than returning a partial structure
      silently. A clause line with no matching section is still captured
      (not silently dropped) under an "UNSECTIONED" bucket so nothing from
      the source is ever lost during parsing.

  - name: summarize_policy
    description: Takes the structured sections/clauses from retrieve_policy and produces a compliant summary text preserving every clause and every condition, with clause references, grouped by section.
    input: The list of section dicts returned by retrieve_policy.
    output: >
      A plain-text string: a section-by-section digest where every clause
      number from the input appears exactly once, prefixed by its number,
      with all of its conditions retained. Clauses whose obligation
      includes multiple conditions (e.g. "Department Head AND HR
      Director") are never compressed to a single condition.
    error_handling: >
      If a clause's text is empty or unparseable, the skill does not skip
      it — it emits the clause number with a "[COULD NOT BE SUMMARISED —
      SEE SOURCE CLAUSE N.N]" marker rather than silently omitting it, so
      the completeness check (one entry per source clause) always passes
      for a fully-formed input and only ever fails loudly, never silently.
