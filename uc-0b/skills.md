# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and returns its content as structured numbered sections.
    input: Path to a policy text file (string), e.g. ../data/policy-documents/policy_hr_leave.txt.
    output: Structured object mapping section headers (e.g. "2. ANNUAL LEAVE") to their numbered clauses (e.g. {"2.3": "Employees must submit a leave application at least 14 calendar days in advance using Form HR-L1."}).
    error_handling: If the file is missing, unreadable, or contains no numbered clauses, return an explicit error and do not fabricate content.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary referencing clauses by number.
    input: Structured sections from retrieve_policy.
    output: Summary covering every clause, each bullet tagged with its clause number (e.g. "2.3: ...") and preserving all obligations, binding verbs, and multi-condition requirements verbatim in meaning.
    error_handling: If any clause is ambiguous or cannot be summarised without losing meaning, quote it verbatim and flag it; if a clause is missing from the input, report it rather than guess.
