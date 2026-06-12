# skills.md — UC-0B Policy Summarisation Agent

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy file and parses it into a structured dict of sections, each containing numbered clauses mapped to their full text.
    input: >
      file_path (str) — absolute or relative path to a .txt policy document.
      Expected structure: section headings separated by divider lines (═══), clauses numbered
      as X.Y (e.g. 2.3, 5.2), with clause body text on the same or following indented lines.
    output: >
      A dict of the form:
        {
          "title": str,                          # document title (first non-empty lines)
          "reference": str,                      # document reference code if present
          "sections": {
            "2": {
              "heading": "ANNUAL LEAVE",
              "clauses": {
                "2.1": "Each permanent employee is entitled to...",
                "2.3": "Employees must submit a leave application..."
              }
            },
            ...
          }
        }
    error_handling: >
      If file_path does not exist: raise FileNotFoundError with the path.
      If the file is empty: raise ValueError("Policy file is empty: {path}").
      If no numbered clauses are found: raise ValueError("No clauses parsed — check document format").
      Malformed lines (no clause number) are collected into the previous clause's text; never silently dropped.

  - name: summarize_policy
    description: Takes the structured policy dict from retrieve_policy and produces a clause-complete, obligation-faithful plain-text summary, validating all mandated clauses are present and no binding verb is softened.
    input: >
      policy (dict) — the structured dict returned by retrieve_policy.
      mandatory_clauses (list[str]) — list of clause IDs that MUST appear in output
        (e.g. ["2.3", "2.4", "2.5", "2.6", "2.7", "3.2", "3.4", "5.2", "5.3", "7.2"]).
    output: >
      A plain-text string structured as:
        - Document header (title, reference, version)
        - One section block per section, with heading
        - Each clause on its own line: "[X.Y] <faithful summary or [VERBATIM] quote>"
        - A VALIDATION REPORT at the end listing:
            * PRESENT: clauses found in output
            * MISSING: mandatory clauses absent from output (empty if all present)
            * FLAGS: clauses tagged [VERBATIM] or [FLAG: meaning-loss risk]
    error_handling: >
      If a mandatory clause ID is not found in the parsed policy dict:
        emit a WARNING line in the VALIDATION REPORT: "MISSING clause X.Y — not found in source document".
      If binding verb softening is detected (heuristic check):
        append [SOFTENING-RISK] tag to that clause line and list it in FLAGS.
      Never raise an exception mid-summary — always produce partial output with a VALIDATION REPORT
      so failures are visible, not silent.
