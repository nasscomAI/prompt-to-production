# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and returns its content as structured numbered sections.
    input: Path to a plain-text policy file (string), e.g. ../data/policy-documents/policy_hr_leave.txt
    output: Structured list of sections, each with a section number, heading, and numbered clauses (e.g. [{section: "2", title: "ANNUAL LEAVE", clauses: [{id: "2.3", text: "..."}]}]).
    error_handling: Returns a clear error if the file path is invalid, the file is not .txt, or the content cannot be split into numbered clauses; it never fabricates clause numbers.

  - name: summarize_policy
    description: Takes the structured clauses from retrieve_policy and produces a compliant summary that preserves every clause and every condition.
    input: Structured numbered sections as returned by retrieve_policy.
    output: A summary with one entry per clause, each referenced by its clause number; any clause that resists faithful summary is quoted verbatim and explicitly flagged.
    error_handling: If any clause is missing from the summary or any condition was dropped, it reports the specific clause and the dropped condition rather than silently returning an incomplete summary.
