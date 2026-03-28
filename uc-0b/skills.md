# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Load and parse an HR leave policy text file into structured numbered clauses.
    input: string path to policy text file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: dict mapping clause numbers (e.g. 2.3) to clause text strings.
    error_handling: if file is missing/unreadable, raise an exception; if parsing fails partially, include extracted clauses and record missing ones for downstream handling.

  - name: summarize_policy
    description: Generate a clause-preserving summary from structured clause sections.
    input: dict of structured numbered clauses from retrieve_policy.
    output: text summary with each required clause referenced and a missing-clause report if needed.
    error_handling: if required clauses are missing, include placeholder warnings; if meaning could be lost (multi-condition rules), emit verbatim clause text with explicit warning or flag.


