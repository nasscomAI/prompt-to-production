# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections keyed by clause number.
    input: A file path to a policy document (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: An ordered mapping of clause number (e.g. "2.3") to the clause text with its binding verb intact.
    error_handling: If the file is missing or unreadable, raises a clear error. If a clause number cannot be extracted, keeps the raw text under a section marker rather than dropping it.

  - name: summarize_policy
    description: Takes the structured clauses and produces a complete, faithful summary with per-clause references.
    input: The structured output of retrieve_policy plus the list of clause numbers that must be covered (the ground-truth inventory).
    output: A summary_hr_leave.txt file where every required clause appears under its clause number with all conditions and the binding verb preserved.
    error_handling: If a required clause is missing from the input, does not silently skip it — it is quoted verbatim and flagged. If an obligation cannot be reworded without meaning loss, it is left verbatim and flagged.