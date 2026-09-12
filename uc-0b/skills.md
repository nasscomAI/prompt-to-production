# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: >
      Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      Path to a policy .txt file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: >
      Ordered list of sections, each with clause number (e.g. "2.3") and its full text.
    error_handling: >
      Raises a clear error if the file is missing; warns and reports any clause that
      could not be parsed into a numbered section.

  - name: summarize_policy
    description: >
      Produces a compliant clause-referenced summary from the structured sections.
    input: >
      The structured sections returned by retrieve_policy.
    output: >
      Summary text where every numbered clause is present with its clause reference
      and all conditions preserved.
    error_handling: >
      If a clause cannot be summarised without meaning loss, quotes it verbatim and
      appends a flag (e.g. "QUOTED VERBATIM — could not compress without changing meaning").