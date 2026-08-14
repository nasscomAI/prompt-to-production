# skills.md

skills:
  - name: retrieve_policy
    description: Loads the policy .txt file and returns its content as structured numbered sections for clause-by-clause summarisation.
    input: Path to a policy text file (e.g. ../data/policy-documents/policy_hr_leave.txt).
    output: An ordered list of sections keyed by clause number (2.3, 2.4, ... 7.2), each with its full original text, preserving binding verbs exactly as written.
    error_handling: If a numbered clause cannot be parsed into a clean section, returns the raw text for that range and flags the clause number — it never silently drops a clause.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that references every clause and preserves all conditions.
    input: The structured sections from retrieve_policy, plus the 10-clause ground-truth inventory from the README (clause number, core obligation, binding verb).
    output: A summary (summary_hr_leave.txt) where all 10 clauses are present with their binding verbs, every multi-condition obligation keeps ALL conditions (e.g. 5.2 names both Department Head AND HR Director), and every entry references its clause number.
    error_handling: If a clause's obligation cannot be preserved without meaning loss, quotes it verbatim and flags the clause number as UNSUMMARISABLE instead of softening, merging, or dropping it. Never adds statements not present in the source. Reports a checklist of which clauses were covered and which were flagged.
