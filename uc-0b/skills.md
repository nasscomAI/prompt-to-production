# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads the .txt policy file and parses it into structured numbered
      sections, preserving every clause number, heading, and full text.
    input: >
      input_path (str) — absolute or relative path to the policy .txt file
      (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A list of dicts, each containing: section_number (str, e.g. "2.3"),
      section_heading (str, e.g. "ANNUAL LEAVE"), and text (str — the
      full clause text exactly as it appears in the source).
    error_handling: >
      If the file does not exist or cannot be read, print an error message
      and exit. If a line cannot be parsed into a section, preserve it as
      raw text under the current section heading. Never silently drop
      content.

  - name: summarize_policy
    description: >
      Takes the structured sections from retrieve_policy and produces a
      compliant summary with clause references. Every numbered clause
      from the source is included. All thresholds, deadlines, conditions,
      AND/OR relationships, binding verbs, and prohibitions are preserved
      exactly as stated in the source.
    input: >
      sections (list of dicts from retrieve_policy) — the full parsed
      policy content.
    output: >
      A string containing the complete summary, organized by section
      headings, with every clause referenced by number. Written to the
      output file specified by --output.
    error_handling: >
      If a clause cannot be summarized without meaning loss, the full
      source text is quoted verbatim with the clause number. If sections
      are empty, the output notes "No content found in section." Never
      invent content. Never omit a clause.
