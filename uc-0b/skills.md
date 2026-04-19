# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Reads a raw text policy document and parses it into a structured list of numbered sections and clauses (e.g., 2.3, 5.2).
    input: File path to a .txt policy document (e.g., policy_hr_leave.txt).
    output: A collection of clause-specific records, each containing the clause index and its corresponding raw text body.
    error_handling: Refuses input if the document lacks numbered sections or if the file encoding is incompatible.

  - name: summarize_policy
    description: Condenses each policy clause into a concise summary while ensuring no "binding verbs" or multi-approval conditions are omitted.
    input: A list of structured clause records.
    output: A formatted text summary where every numbered clause is referenced and all core obligations are preserved.
    error_handling: If a clause's complexity risks meaning loss, it is included as a verbatim quote flagged with a [LITERAL] marker.
