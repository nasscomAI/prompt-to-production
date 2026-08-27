# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and parses it into a structured inventory of numbered clauses and their original text.
    input: Absolute path to a .txt policy file (e.g., policy_hr_leave.txt).
    output: A structured collection mapping clause numbers to their verbatim content.
    error_handling: Refuse processing if the file is missing or contains no identifiable numbered clauses.

  - name: summarize_policy
    description: Produces a high-fidelity summary of structured clauses, ensuring 100% obligation preservation and zero scope bleed.
    input: Structured clause data from retrieve_policy.
    output: A summary text with numbered clause references, preserving all binding language and multi-condition rules.
    error_handling: Flags clauses for verbatim quoting if they cannot be reduced without meaning loss; errors if any clause is omitted or conditions are softened.

