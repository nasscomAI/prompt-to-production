# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Reads a .txt policy file from disk and returns the content as a
      structured list of numbered sections and clauses. Handles separator
      lines (═══) and section headers. Returns a dict mapping section
      numbers to lists of clause dicts with keys: number, text.
    input: >
      str — file path to a .txt policy document
    output: >
      dict — {section_number: [{clause_number, text}, ...]}
    error_handling: >
      If file is missing or unreadable, raises FileNotFoundError. If the
      file contains no parseable clauses, returns {"0": [{"0": "Unparseable
      content"}]. Never crashes on malformed lines.

  - name: summarize_policy
    description: >
      Takes a structured policy dict and produces a plain-text summary
      string. Every numbered clause appears exactly once. Multi-condition
      obligations list all conditions. Binding verbs are preserved. Clauses
      too complex to summarise are quoted verbatim and flagged [VERBATIM].
    input: >
      dict — structured policy from retrieve_policy
    output: >
      str — plain-text summary with section headers and clause references
    error_handling: >
      If input is empty, returns "No clauses to summarise." If a clause
      text is None or empty, outputs "[Clause X — empty]" as a placeholder.
      Never produces hallucinated content.
