# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns its content as a structured string with preserved clause numbering.
    input: String path to .txt policy file (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: String containing the full policy text with all sections, clause numbers, and formatting preserved.
    error_handling: Raises FileNotFoundError if file doesn't exist. Raises IOError if file cannot be read. Returns error message to stderr and exits with non-zero code.

  - name: summarize_policy
    description: Generates a faithful summary of policy content preserving all critical clauses, binding verbs, and multi-condition obligations without adding external context.
    input: String containing structured policy text with numbered clauses.
    output: String summary organized by section, with all 10 critical clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) preserved with their complete conditions and binding verbs. Each clause must include its clause number.
    error_handling: If any of the 10 critical clauses cannot be found in input, includes a WARNING section listing missing clauses. If a clause has complex conditions that could lose meaning when summarized, quotes it verbatim with [QUOTED] marker.
