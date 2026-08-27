skills:
  - name: retrieve_policy
    description: Load the HR leave policy text file and return its contents as structured, numbered sections.
    input: Path to the policy file (e.g. `../data/policy-documents/policy_hr_leave.txt`) as a string.
    output: Structured representation of the policy as an ordered list or mapping of section and clause identifiers (e.g. 2.3, 2.4, …, 7.2) to their full original text.
    error_handling: If the file cannot be found, read, or parsed into numbered sections, return a clear error object/message describing the issue and do not fabricate sections or clauses.

  - name: summarize_policy
    description: Take structured policy sections and produce a compliant summary that preserves all obligations and conditions with explicit clause references.
    input: Structured policy representation (e.g. list or mapping of clause IDs to text) plus a clause inventory specifying required clauses (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2).
    output: A textual summary that: (a) covers each required clause with its core obligation and conditions intact, (b) includes clause identifiers, and (c) clearly flags any clauses that must be quoted verbatim due to potential meaning loss.
    error_handling: If any required clause is missing, ambiguous, or cannot be safely summarised without dropping conditions, the skill must (a) refuse to guess, (b) quote the problematic clause verbatim, and (c) return a machine-checkable indication of which clauses could not be safely summarised.
