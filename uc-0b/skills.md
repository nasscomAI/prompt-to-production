# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file from disk and returns its content as an ordered
      list of numbered sections, preserving clause numbers and binding language.
    input: >
      A string: the file path to a .txt policy document
      (e.g. "../data/policy-documents/policy_hr_leave.txt").
    output: >
      A list of dicts, one per section, each with:
        - section_number (string): e.g. "2.3", "5.2"
        - section_title (string): The heading text if present, else empty string.
        - section_text (string): The full text of the section, unmodified.
      Returned in document order. Top-level sections and sub-sections are
      both included as separate entries.
    error_handling: >
      If the file does not exist: raise FileNotFoundError with the path included
      in the message. Do not return a partial result.
      If the file is empty: return an empty list and print a warning to stdout.
      If section numbers cannot be parsed: include the text as a single entry
      with section_number set to "UNPARSED" and log to stdout. Never silently
      discard text.

  - name: summarize_policy
    description: >
      Takes the structured list of sections from retrieve_policy and produces
      a clause-by-clause summary that preserves all obligations, binding verbs,
      and multi-condition requirements exactly as they appear in the source.
    input: >
      A list of section dicts as returned by retrieve_policy (section_number,
      section_title, section_text).
    output: >
      A string: the formatted policy summary. Each clause is rendered as:
        [CLAUSE {section_number}] {summary text}
      If a clause is quoted verbatim due to meaning-loss risk, it is rendered as:
        [CLAUSE {section_number}] [VERBATIM] "{exact clause text}"
      Clauses appear in the same order as the input sections.
    error_handling: >
      If input list is empty: return the string "No clauses found in document."
      If a section's text is empty or whitespace only: skip it and log a warning
      to stdout with the section_number.
      If summarisation of a clause would require omitting a condition or binding
      verb: fall back to verbatim quoting for that clause and append [VERBATIM].
      Never silently drop a clause — every entry in the input must produce an
      entry in the output.
