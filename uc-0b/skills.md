# skills.md

skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and returns its content as structured numbered sections.
    input: Path to a policy text file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: An ordered list of sections keyed by clause number (2.3, 2.4, ... 7.2), each with its full original text.
    error_handling: If a numbered clause cannot be parsed into a clean section, returns the raw text for that range and flags it — it never silently drops a clause.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary with clause references and preserved obligations.
    input: The structured sections from retrieve_policy, plus the 10-clause ground-truth inventory from the README.
    output: A summary (summary_hr_leave.txt) where every clause is present, every multi-condition obligation keeps all conditions, and every entry references its clause number.
    error_handling: If a clause's obligation cannot be preserved without meaning loss, quotes it verbatim and flags it as UNSUMMARISABLE instead of softening or dropping it. Never adds statements that are not present in the source.
