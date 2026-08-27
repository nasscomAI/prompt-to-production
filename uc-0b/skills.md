skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: File path (string) pointing to a plain-text policy document (e.g. policy_hr_leave.txt).
    output: Structured text with each numbered clause preserved as a discrete section, retaining original clause numbers and wording.
    error_handling: If the file is missing, unreadable, or contains no numbered clauses, raise an error and halt — do not proceed with empty or partial content.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that references every clause with its binding verb and all conditions intact.
    input: Structured numbered sections returned by retrieve_policy (text).
    output: Plain-text summary where each of the 10 clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) is explicitly referenced with its binding verb and no conditions dropped.
    error_handling: If a clause cannot be summarised without meaning loss, quote it verbatim and flag it rather than paraphrasing; never infer or add information not present in the source.
