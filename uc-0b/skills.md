# skills.md — UC-0B Policy Summary Skills

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and parses its contents into structured numbered sections and clauses.
    input: File path input_path (str, e.g. path to policy_hr_leave.txt).
    output: List of section objects containing section titles, clause numbers (e.g. 2.3, 5.2), binding verbs, and raw clause text.
    error_handling: Raises FileNotFoundError if input path is invalid; returns error flag if file content is empty or unreadable.

  - name: summarize_policy
    description: Processes structured policy sections into a high-fidelity summary adhering to RICE enforcement rules without clause omission or obligation softening.
    input: Structured policy sections data structure from retrieve_policy.
    output: Formatted text summary string containing explicit clause citations, multi-condition approval rules, and flagged verbatim quotes.
    error_handling: Flags missing clauses or ambiguous multi-approver requirements with explicit warning tags in the final summary.

