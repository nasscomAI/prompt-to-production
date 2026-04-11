# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses it into structured numbered sections with their content.
    input: >
      A file path (string) pointing to a .txt policy document.
      Example: "../data/policy-documents/policy_hr_leave.txt"
    output: >
      A list of section objects, each containing:
        - section_number (string): The clause number, e.g. "2.3", "5.2"
        - section_title (string): The section heading if present, e.g. "ANNUAL LEAVE"
        - content (string): The full text of the clause
      Example: [{"section_number": "2.3", "section_title": "ANNUAL LEAVE", "content": "Employees must submit..."}]
    error_handling: >
      If the file does not exist or cannot be read, raise a clear error message
      and exit. If the file is empty or contains no numbered clauses, report
      "No structured clauses found" and exit with an error.

  - name: summarize_policy
    description: Takes structured policy sections and produces a faithful clause-by-clause summary preserving all obligations, conditions, and binding verbs.
    input: >
      A list of section objects as produced by retrieve_policy.
    output: >
      A plain-text summary where each clause is summarized on one or two lines,
      prefixed with its original clause number. Binding verbs are preserved exactly.
      Multi-condition obligations retain all conditions. No external information is added.
      Clauses that cannot be summarized without meaning loss are quoted verbatim
      with a [VERBATIM] prefix.
      Example output line: "2.3: Employees must submit leave application at least 14 calendar days in advance using Form HR-L1."
    error_handling: >
      If a section has no content or is malformed, include it in the output with
      a note: "[EMPTY CLAUSE — no content found in source]". Never silently skip
      a clause.
