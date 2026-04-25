# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a structured list of numbered clauses to facilitate ground-truth mapping.
    input: Path to the input policy file (e.g., '../data/policy-documents/policy-hr-leave.txt').
    output: A collection of structured sections, where each element contains the clause number and the verbatim clause text.
    error_handling: Return a clear error if the file path is invalid, the file is unreadable, or no numbered clauses (e.g., "2.3") are detected.

  - name: summarize_policy
    description: Processes structured policy clauses to produce a compliant summary that preserves all multi-condition obligations and includes explicit clause references.
    input: Structured clause data from the `retrieve_policy` skill.
    output: Path to the generated results summary file (e.g., 'summary_hr_leave.txt').
    error_handling: If a clause cannot be summarized without losing critical nuance (binding verbs or dual-approver conditions), the skill must output the verbatim clause text flagged as "High Fidelity Quote".

