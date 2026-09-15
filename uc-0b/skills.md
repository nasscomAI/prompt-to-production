skills:
  - name: retrieve_policy
    description: Reads the raw policy text file from disk and parses it into clean, structured sections indexed by section numbers.
    input: File path to policy text file (e.g., policy_hr_leave.txt).
    output: Structured string or list containing full section texts mapped to clause identifiers.
    error_handling: Raises FileNotFoundError if the file cannot be located at the provided path.

  - name: summarize_policy
    description: Processes structured policy text using strict anti-softening and condition-preservation rules to generate an auditable summary.
    input: Structured policy text sections.
    output: Text summary covering all 10 key clauses with explicit section citations, preserved dual-approvers, and retained binding verbs.
    error_handling: Falls back to verbatim section extraction if summarization risks condition omission.