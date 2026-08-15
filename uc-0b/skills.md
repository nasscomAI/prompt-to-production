# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with their clauses, preserving verbatim text.
    input: Path to a policy file, e.g. ../data/policy-documents/policy_hr_leave.txt.
    output: A tuple of (header_lines, sections) where each section holds its title and a list of (clause_number, clause_text) pairs with the original wording intact.
    error_handling: Raises a clear error if the file is missing or unreadable; skips decorative lines (separators, title blocks) rather than guessing at their meaning.

  - name: summarize_policy
    description: Produces a clause-faithful summary with clause references, covering every numbered clause and preserving every condition.
    input: Structured sections from retrieve_policy.
    output: Plain-text summary written to uc-0b/summary_hr_leave.txt with one line per clause, all clauses present, nothing added.
    error_handling: If any clause cannot be condensed without meaning loss, quotes it verbatim and flags it as [QUOTED] instead of paraphrasing; reports a warning if any inventory clause is missing from the output.
