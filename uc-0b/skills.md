# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered clauses.
    input: Path to a .txt policy document (e.g., policy_hr_leave.txt).
    output: A list of objects, each containing a clause number and its literal text content.
    error_handling: If the file format is not .txt or is empty, return an error message and stop processing.

  - name: summarize_policy
    description: Generates a high-fidelity summary for each parsed clause while preserving all legal obligations and conditions.
    input: A list of structured policy clauses from `retrieve_policy`.
    output: A formatted string containing the summary of each clause with its original numbering.
    error_handling: If a clause is missing a core obligation or binding verb, flag it as 'COMPLEX_CLAUSE' and quote it verbatim.
