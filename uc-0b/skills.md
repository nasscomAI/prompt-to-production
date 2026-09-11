skills:
  - name: retrieve_policy
    description: Loads the HR policy .txt file and returns its content as structured numbered sections matching the clause numbering in the source.
    input: "Path to policy_hr_leave.txt."
    output: "A list of sections, each with clause number (e.g. '2.3') and the exact clause text."
    error_handling: >
      If the file is missing or unreadable, raise a clear error and stop.
      If a clause cannot be matched to a number (malformed numbering), include
      it as an unnumbered section rather than dropping it silently.

  - name: summarize_policy
    description: Produces a compliant summary of the retrieved policy sections, preserving every clause and all of its conditions.
    input: "The structured list of numbered clause sections from retrieve_policy."
    output: "A text summary with one line per clause, each prefixed by its clause number, preserving the binding verb and all conditions."
    error_handling: >
      If a clause has multiple conditions (e.g. two required approvers), all
      conditions must appear in the summary line — never collapse to a single
      condition. If a clause cannot be safely shortened without losing meaning,
      output the clause verbatim instead of a paraphrase, marked with a
      [VERBATIM] flag.