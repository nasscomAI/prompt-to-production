# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Load a .txt policy file and return it as structured sections of numbered clauses.
    input: Path to a policy text file (e.g. policy_hr_leave.txt).
    output: A list of sections, each with a title and a list of clauses; every clause has a number
      (X.Y) and its full text with wrapped lines rejoined.
    error_handling: Raises a clear error if the file is missing or contains no numbered clauses;
      never silently skips an unparseable clause.

  - name: summarize_policy
    description: Produce a compliant clause-complete summary from the structured sections.
    input: The structured sections returned by retrieve_policy.
    output: A string summary containing every numbered clause, section by section, with conditions
      fully preserved; clauses that cannot be condensed without meaning loss are quoted verbatim
      and flagged as quoted-verbatim.
    error_handling: Verifies every parsed clause number appears in the output; if any clause is
      missing from the summary, it raises instead of writing an incomplete file.
